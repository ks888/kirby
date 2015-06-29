
import os
import re
import subprocess


class ServerspecRunner(object):
    """Run serverspec command and retrieve its results"""
    pattern = re.compile(r'(\d+) examples, (\d+) failures')

    def __init__(self, serverspec_dir, serverspec_cmd):
        self.serverspec_dir = serverspec_dir
        self.serverspec_cmd = serverspec_cmd

    def run(self):
        orig_dir = os.getcwd()
        os.chdir(self.serverspec_dir)

        try:
            cmd_result = subprocess.check_output(self.serverspec_cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            cmd_result = ex.output

        os.chdir(orig_dir)

        match_result = ServerspecRunner.pattern.search(cmd_result)
        num_test = int(match_result.group(1))
        num_failed_test = int(match_result.group(2))

        return (num_test, num_failed_test)
