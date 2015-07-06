
from mock import patch
import unittest

from kirby.callback_plugins.analyze_coverage import CallbackModule


class AnalyzeCoverageTest(unittest.TestCase):
    @patch.dict('os.environ', {'KIRBY_CONFIG': './sample.conf'})
    @patch('subprocess.check_output', return_value="2 examples, 2 failures")
    def test_playbook_on_start(self, mock_subprocess):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 2)

    def test_playbook_on_start_use_default_values(self):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertEqual(callbacks.setting_manager.enable_kirby, False)
