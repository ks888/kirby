
import os

from kirby.serverspec_runner import ServerspecRunner
from kirby.setting_manager import SettingManager


class CallbackModule(object):
    """Plugin for analyzing task coverage"""

    def __init__(self):
        self.num_changed_tasks = 0
        self.num_tested_tasks = 0
        self.not_tested_tasks = []

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
        if self.setting_manager.enable_kirby:
            self.curr_task_name = 'setup'

    def playbook_on_task_start(self, name, is_conditional):
        if self.setting_manager.enable_kirby:
            self.curr_task_name = name

    def runner_on_ok(self, host, res):
        if self.setting_manager.enable_kirby:
            if res['changed']:
                self.runner = ServerspecRunner(self.setting_manager.serverspec_dir,
                                               self.setting_manager.serverspec_cmd)
                result = self.runner.run()

                self.num_changed_tasks += 1
                if result[1] < self.num_failed_tests:
                    self.num_tested_tasks += 1
                else:
                    self.not_tested_tasks += [self.curr_task_name]

                self.num_tests = result[0]
                self.num_failed_tests = result[1]

    def playbook_on_stats(self, stats):
        print "playbook_on_stats"
