
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

    @patch('subprocess.check_output', return_value='2 examples, 2 failures')
    def testPlaybookOnStart_RunnerSuccessful_KirbyIsEnabled(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertTrue(callbacks.setting_manager.enable_kirby)

    @patch('subprocess.check_output', return_value='')
    def testPlaybookOnStart_RunnerFailure_KirbyIsDisabled(self, mock_subprocess):
        devnull = open(os.devnull, 'w')
        with patch('sys.stderr', devnull):
            callbacks = CallbackModule()
            callbacks.playbook_on_start()

        self.assertFalse(callbacks.setting_manager.enable_kirby)

    def testPlaybookOnSetup_KirbyIsEnabled_TaskNameSet(self):
        callbacks = CallbackModule()
        callbacks.playbook_on_setup()

        self.assertEqual(callbacks.curr_task_name, 'setup')

    def testPlaybookOnTaskStart_KirbyIsEnabled_TaskNameSet(self):
        callbacks = CallbackModule()
        callbacks.playbook_on_task_start('it\'s me', False)

        self.assertEqual(callbacks.curr_task_name, 'it\'s me')

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures\nrspec 1\nrspec 2', '2 examples, 1 failure\nrspec 2'])
    @patch('sys.stdout', new_callable=StringIO)
    def testRunnerOnOk_ChangedAndTestedTask_ShowTestedBy(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        result = mock_stdout.getvalue()
        self.assertIn('tested by:', result)
        self.assertIn('rspec 1', result)

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures', '2 examples, 1 failure'])
    @patch('sys.stdout', new_callable=StringIO)
    def testRunnerOnOk_ChangedAndTestedTask_IncNumTestedTasks(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        self.assertEqual(callbacks.num_tested_tasks, 1)
        self.assertEqual(callbacks.not_tested_tasks, [])

    @patch('subprocess.check_output', side_effect=['2 examples, 1 failure\nrspec 1', '2 examples, 1 failure\nrspec 1'])
    @patch('sys.stdout', new_callable=StringIO)
    def testRunnerOnOk_ChangedAndNotTestedTask_ShowTestedBy(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        result = mock_stdout.getvalue()
        self.assertIn('tested by:', result)
        self.assertNotIn('rspec', result)

    @patch('subprocess.check_output', side_effect=['2 examples, 1 failure', '2 examples, 1 failure'])
    @patch('sys.stdout', new_callable=StringIO)
    def testRunnerOnOk_ChangedAndNotTestedTask_AddToFailTasks(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        self.assertEqual(callbacks.num_tested_tasks, 0)
        self.assertEqual(callbacks.not_tested_tasks, ['it\'s me'])

    @patch('subprocess.check_output', side_effect=['2 examples, 1 failure', '2 examples, 1 failure'])
    def testRunnerOnOk_CoverageSkipTask_NotIncNumChangedTasks(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me (coverage_skip)', False)
        callbacks.runner_on_ok('localhost', {'changed': True})

        self.assertEqual(callbacks.num_changed_tasks, 0)

    def testRunnerOnOk_ChangedNotDefinedTask_RunnerNotCalled(self):
        callbacks = CallbackModule()
        # want to use runner.run.call_count for assertion
        callbacks.runner.run = MagicMock(side_effect=[(0, 0, []), None])
        callbacks.runner_on_ok('localhost', {})

        self.assertEqual(callbacks.runner.run.call_count, 0)

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures', '2 examples, 0 failure'])
    @patch('sys.stdout', new_callable=StringIO)
    def testPlaybookOnStats_AllTestedTask_Coverage100(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})
        callbacks.playbook_on_stats(None)

        result = mock_stdout.getvalue()
        self.assertIn(' 100%', result)
        self.assertNotIn('Not covered:', result)
        self.assertNotIn('WARNING:', result)

    @patch('subprocess.check_output', side_effect=['2 examples, 2 failures', '2 examples, 2 failure'])
    @patch('sys.stdout', new_callable=StringIO)
    def testPlaybookOnStats_NoTestedTask_Coverage0(self, mock_stdout, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()
        callbacks.playbook_on_task_start('it\'s me', False)
        callbacks.runner_on_ok('localhost', {'changed': True})
        callbacks.playbook_on_stats(None)

        result = mock_stdout.getvalue()
        self.assertIn(' 0%', result)
        self.assertIn('it\'s me', result)
        self.assertIn('WARNING:', result)
