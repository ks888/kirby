
from mock import patch
import os
import subprocess
import sys
import unittest

sys.path.append(os.getcwd() + '/../..')
from callback_plugins.kirby import ServerspecRunner


class ServerspecRunnerTest(unittest.TestCase):
    def setUp(self):
        self.runner = ServerspecRunner('.', '')

    @patch('subprocess.check_output', return_value="2 examples, 0 failures")
    def test_run_successful(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (2, 0, []))

    @patch('subprocess.check_output',
           side_effect=subprocess.CalledProcessError(1, '', output="1 example, 1 failure\nrspec ..."))
    def test_run_failure(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (1, 1, ['rspec ...']))

    @patch('subprocess.check_output',
           side_effect=subprocess.CalledProcessError(1, '', output=""))
    def test_run_empty_output(self, mock):
        result = self.runner.run()
        self.assertIsNone(result)

    @patch('subprocess.check_output',
           side_effect=subprocess.CalledProcessError(1, '', output="100 examples, 99 failures"))
    def test_run_100tests(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (100, 99, []))

    @patch('subprocess.check_output',
           side_effect=subprocess.CalledProcessError(1, '', output="2 examples, 2 failures\nrspec ... rspec ...\nrspec ..."))
    def test_run_2_failed_tests(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (2, 2, ['rspec ... rspec ...', 'rspec ...']))
