
from mock import patch
import unittest

from kirby.serverspec_runner import ServerspecRunner


class ServerspecRunnerTest(unittest.TestCase):
    def setUp(self):
        self.runner = ServerspecRunner('.', '')

    @patch('subprocess.check_output', return_value="2 examples, 0 failures")
    def test_run_successful(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (2, 0))

    @patch('subprocess.check_output', return_value="2 examples, 1 failures")
    def test_run_failure(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (2, 1))

    @patch('subprocess.check_output', return_value="100 examples, 99 failures")
    def test_run_100tests(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (100, 99))
