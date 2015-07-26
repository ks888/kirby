
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

    @patch('subprocess.check_output', return_value="1 example, 0 failures")
    def testRun_NoFailedTest_NumTestsIsSet(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (1, 0, []))

    @patch('subprocess.check_output',
           side_effect=subprocess.CalledProcessError(1, '', output="1 example, 1 failure\nrspec ..."))
    def testRun_Has1FailedTest_FailedTestIsSet(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (1, 1, ['rspec ...']))

    @patch('subprocess.check_output',
           side_effect=subprocess.CalledProcessError(1, '', output="2 examples, 2 failures\nrspec ... rspec ...\nrspec ..."))
    def testRun_Has2FailedTests_FailedTestIsSet(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (2, 2, ['rspec ... rspec ...', 'rspec ...']))

    @patch('subprocess.check_output',
           side_effect=subprocess.CalledProcessError(1, '', output=""))
    def testRun_InvalidOutput_ReturnNone(self, mock):
        result = self.runner.run()
        self.assertIsNone(result)

    @patch('subprocess.check_output',
           side_effect=subprocess.CalledProcessError(1, '', output="100 examples, 99 failures"))
    def testRun_LargeNumOfTests_CaptureCorrectly(self, mock):
        result = self.runner.run()
        self.assertTupleEqual(result, (100, 99, []))

    def testRun_DirectoryIsNone_ReturnNone(self):
        self.runner.serverspec_dir = None
        result = self.runner.run()

        self.assertIsNone(result)
