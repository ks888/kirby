
from StringIO import StringIO
from mock import patch
from mock import MagicMock
import os
import sys
import unittest

sys.path.append(os.getcwd() + '/../..')
from callback_plugins.kirby import CallbackModule
import utils


class AnalyzeCoverageTest(unittest.TestCase):
    def setUp(self):
        utils.reset_kirby_env_vars()

    @patch.dict('os.environ',
                {'KIRBY_ENABLE': 'yes', 'KIRBY_SERVERSPEC_DIR': '', 'KIRBY_SERVERSPEC_CMD': ''})
    def test_init_empty_env_var(self):
        devnull = open(os.devnull, 'w')
        with patch('sys.stdout', devnull):
            with patch('sys.stderr', devnull):
                callbacks = CallbackModule()

        self.assertTrue(callbacks.setting_manager.enable_kirby)

    @patch.dict('os.environ', {'KIRBY_CONFIG': './empty.cfg'})
    def test_init_not_enough_options(self):
        devnull = open(os.devnull, 'w')
        with patch('sys.stdout', devnull):
            with patch('sys.stderr', devnull):
                callbacks = CallbackModule()

        self.assertFalse(callbacks.setting_manager.enable_kirby)

    def test_init_use_default_config_file(self):
        # default config file (kirby.cfg) will be used
        callbacks = CallbackModule()

        self.assertTrue(callbacks.setting_manager.enable_kirby)

    @patch('subprocess.check_output', return_value='2 examples, 2 failures')
    def test_playbook_on_start(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 2)

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

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures', '2 examples, 1 failures'])
    def test_runner_on_ok_tested_case(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 1)

        self.assertEqual(callbacks.num_changed_tasks, 1)
        self.assertEqual(callbacks.num_tested_tasks, 1)

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures', '2 examples, 2 failures'])
    def test_runner_on_ok_not_tested_case(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 2)

        self.assertEqual(callbacks.num_changed_tasks, 1)
        self.assertEqual(callbacks.num_tested_tasks, 0)
        self.assertListEqual(callbacks.not_tested_tasks, ['it\'s me'])

    def test_runner_on_ok_changed_not_defined(self):
        callbacks = CallbackModule()
        callbacks.runner.run = MagicMock(side_effect=[(0, 0), None])
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {})

        # Only playbook_on_start() should call it
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
