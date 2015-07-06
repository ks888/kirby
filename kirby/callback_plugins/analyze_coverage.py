
import ansible.utils  # unused, but necessary to avoid circular imports
from ansible.callbacks import display
import os

from kirby.serverspec_runner import ServerspecRunner
from kirby.setting_manager import SettingManager


class CallbackModule(object):
    """Plugin for analyzing task coverage"""

    def __init__(self):
        config_file = os.environ.get('KIRBY_CONFIG', None)
        self.setting_manager = SettingManager(config_file)

        if self.setting_manager.enable_kirby:
            self.runner = ServerspecRunner(self.setting_manager.serverspec_dir,
                                           self.setting_manager.serverspec_cmd)

            self.num_changed_tasks = 0
            self.num_tested_tasks = 0
            self.not_tested_tasks = []

    def playbook_on_start(self):
        if self.setting_manager.enable_kirby:
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
                result = self.runner.run()

                self.num_changed_tasks += 1
                if result[1] < self.num_failed_tests:
                    self.num_tested_tasks += 1
                else:
                    self.not_tested_tasks += [self.curr_task_name]

                self.num_tests = result[0]
                self.num_failed_tests = result[1]

    def playbook_on_stats(self, stats):
        if self.setting_manager.enable_kirby:
            display('*** Kirby Results ***')

            coverage = self.num_tested_tasks * 100.0 / self.num_changed_tasks
            display('Coverage: %d / %d (%.1f%%)' % (self.num_tested_tasks, self.num_changed_tasks, coverage))

            if self.num_tested_tasks < self.num_changed_tasks:
                display('Not tested tasks:')
                for task_name in self.not_tested_tasks:
                    display('- %s' % (task_name))

            display('serverspec results: %d / %d' % (self.num_failed_tests, self.num_tests))
            display('*** End ***')
