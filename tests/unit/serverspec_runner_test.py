
import unittest
from kirby.serverspec_runner import ServerspecRunner


class ServerspecRunnerTest(unittest.TestCase):
    def setUp(self):
        self.runner = ServerspecRunner('.', '')

    def test_run(self):
        pass
