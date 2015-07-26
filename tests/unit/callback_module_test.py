
from StringIO import StringIO
from mock import patch
from mock import MagicMock
import os
import sys
import unittest

sys.path.append(os.getcwd() + '/../..')
from callback_plugins.kirby import CallbackModule
import utils


class CallbackModuleTest(unittest.TestCase):
    def setUp(self):
        utils.reset_kirby_env_vars()

    def testInit_UseDefaultConfigFile_KirbyIsEnabled(self):
        # default config file (kirby.cfg) will be used
        callbacks = CallbackModule()

        self.assertTrue(callbacks.setting_manager.enable_kirby)

    @patch.dict('os.environ',
                {'KIRBY_CONFIG': 'kirby_disabled.cfg'})
    def testInit_UseEnvVarSpecifiedConfigFile_KirbyIsDisabled(self):
        callbacks = CallbackModule()

        self.assertFalse(callbacks.setting_manager.enable_kirby)
        # make sure the config file is read
        self.assertEqual(callbacks.setting_manager.serverspec_dir, '/opt')

    @patch.dict('os.environ',
                {'KIRBY_CONFIG': 'notfound.cfg'})
    def testInit_NonExistConfigFile_KirbyIsDisabled(self):
        callbacks = CallbackModule()

        self.assertFalse(callbacks.setting_manager.enable_kirby)

    @patch.dict('os.environ', {'KIRBY_CONFIG': 'kirby_insufficient.cfg'})
    def testInit_InsufficientConfigFile_KirbyIsDisabled(self):
        devnull = open(os.devnull, 'w')
        with patch('sys.stdout', devnull):
            with patch('sys.stderr', devnull):
                callbacks = CallbackModule()

        self.assertFalse(callbacks.setting_manager.enable_kirby)

    @patch('subprocess.check_output', return_value='2 examples, 2 failures\nrspec ...')
    def test_playbook_on_start(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 2)
        self.assertEqual(callbacks.failed_tests, ['rspec ...'])

    @patch('subprocess.check_output', return_value='')
    def test_playbook_on_start_cmd_output_is_empty(self, mock_subprocess):
        devnull = open(os.devnull, 'w')
        with patch('sys.stderr', devnull):
            callbacks = CallbackModule()
            callbacks.playbook_on_start()

        self.assertFalse(callbacks.setting_manager.enable_kirby)

    @patch.dict('os.environ', {'KIRBY_CONFIG': './empty.cfg'})
    def test_playbook_on_start_use_default_values(self):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertEqual(callbacks.setting_manager.enable_kirby, False)

    @patch('subprocess.check_output', return_value='2 examples, 2 failures')
    def test_playbook_on_task_start(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)

        self.assertEqual(callbacks.curr_task_name, 'it\'s me')

    @patch('subprocess.check_output', return_value='2 examples, 2 failures')
    def test_playbook_on_setup(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_setup()

        self.assertEqual(callbacks.curr_task_name, 'setup')

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures\nrspec 1\nrspec 2', '2 examples, 1 failures\nrspec 2'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_runner_on_ok_tested_case(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 1)

        self.assertEqual(callbacks.num_changed_tasks, 1)
        self.assertEqual(callbacks.num_tested_tasks, 1)

        result = mock_stdout.getvalue()
        self.assertIn('tested by:', result)
        self.assertIn('rspec 1', result)

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures\nrspec 1\nrspec 2', '2 examples, 2 failures\nrspec 1\nrspec 2'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_runner_on_ok_not_tested_case(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 2)

        self.assertEqual(callbacks.num_changed_tasks, 1)
        self.assertEqual(callbacks.num_tested_tasks, 0)
        self.assertListEqual(callbacks.not_tested_tasks, ['it\'s me'])

        result = mock_stdout.getvalue()
        self.assertIn('tested by:', result)
        self.assertNotIn('rspec ', result)

    def test_runner_on_ok_changed_not_defined(self):
        callbacks = CallbackModule()
        # want to use runner.run.call_count for assertion
        callbacks.runner.run = MagicMock(side_effect=[(0, 0, []), None])
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {})

        # Only playbook_on_start() should call run()
        self.assertEqual(callbacks.runner.run.call_count, 1)

    @patch('subprocess.check_output', side_effect=['1 examples, 1 failures', '1 examples, 0 failures'])
    def test_runner_on_ok_coverage_ignored(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('dummy task (coverage_skip)', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        self.assertEqual(callbacks.num_tests, 1)
        self.assertEqual(callbacks.num_failed_tests, 0)

        self.assertEqual(callbacks.num_changed_tasks, 0)
        self.assertEqual(callbacks.num_tested_tasks, 0)

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures', '2 examples, 1 failures'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_playbook_on_stats(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})
        callbacks.playbook_on_stats(None)

        result = mock_stdout.getvalue()
        # 1 of 1 changed task is tested
        self.assertIn('100', result)
