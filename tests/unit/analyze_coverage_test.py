
from StringIO import StringIO
from mock import patch
import unittest

from kirby.callback_plugins.analyze_coverage import CallbackModule
import utils


class AnalyzeCoverageTest(unittest.TestCase):
    def setUp(self):
        utils.reset_kirby_env_vars()

    @patch.dict('os.environ', {'KIRBY_CONFIG': './sample.conf'})
    @patch('subprocess.check_output', return_value='2 examples, 2 failures')
    def test_playbook_on_start(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 2)

    def test_playbook_on_start_use_default_values(self):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertEqual(callbacks.setting_manager.enable_kirby, False)

    @patch.dict('os.environ', {'KIRBY_CONFIG': './sample.conf'})
    @patch('subprocess.check_output', return_value='2 examples, 2 failures')
    def test_playbook_on_task_start(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)

        self.assertEqual(callbacks.curr_task_name, 'it\'s me')

    @patch.dict('os.environ', {'KIRBY_CONFIG': './sample.conf'})
    @patch('subprocess.check_output', return_value='2 examples, 2 failures')
    def test_playbook_on_setup(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_setup()

        self.assertEqual(callbacks.curr_task_name, 'setup')

    @patch.dict('os.environ', {'KIRBY_CONFIG': './sample.conf'})
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

    @patch.dict('os.environ', {'KIRBY_CONFIG': './sample.conf'})
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

    @patch.dict('os.environ', {'KIRBY_CONFIG': './sample.conf'})
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
