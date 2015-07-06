
from mock import patch
import unittest

from kirby.callback_plugins.analyze_coverage import CallbackModule


class AnalyzeCoverageTest(unittest.TestCase):
    @patch('subprocess.check_output', return_value="2 examples, 2 failures")
    def test_playbook_on_start(self, mock):
        callbacks = CallbackModule()
        callbacks.playbook_on_start()

        self.assertEqual(callbacks.num_tests, 2)
        self.assertEqual(callbacks.num_failed_tests, 2)
