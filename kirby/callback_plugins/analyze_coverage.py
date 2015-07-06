
import os

from kirby.serverspec_runner import ServerspecRunner
from kirby.setting_manager import SettingManager


class CallbackModule(object):
    """Plugin for analyzing task coverage"""

    def playbook_on_start(self):
        config_file = os.environ.get('KIRBY_CONFIG', None)
        self.setting_manager = SettingManager(config_file)

        if self.setting_manager.enable_kirby:
            self.runner = ServerspecRunner(self.setting_manager.serverspec_dir,
                                           self.setting_manager.serverspec_cmd)

            result = self.runner.run()

            self.num_tests = result[0]
            self.num_failed_tests = result[1]

    def playbook_on_setup(self):
        print "playbook_on_setup"

    def runner_on_ok(self, host, res):
        print "runner_on_ok"

    def playbook_on_task_start(self, name, is_conditional):
        print name

    def playbook_on_stats(self, stats):
        print "playbook_on_stats"
