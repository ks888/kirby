
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

        if self.setting_manager.enable_kirby and not self._check_options():
            display('[kirby] disable kirby...', stderr=True)
            self.setting_manager.enable_kirby = False

        if self.setting_manager.enable_kirby:
            self.runner = ServerspecRunner(self.setting_manager.serverspec_dir,
                                           self.setting_manager.serverspec_cmd)

            self.num_changed_tasks = 0
            self.num_tested_tasks = 0
            self.not_tested_tasks = []

    def _check_options(self):
        manager = self.setting_manager
        if not hasattr(manager, 'serverspec_dir') or manager.serverspec_dir is None:
            display("[kirby] 'serverspec_dir' is not correctly defined")
            return False

        if not hasattr(manager, 'serverspec_cmd') or manager.serverspec_cmd is None:
            display("[kirby] 'serverspec_cmd' is not correctly defined")
            return False

        return True

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

            if self.num_changed_tasks > 0:
                coverage = self.num_tested_tasks * 100.0 / self.num_changed_tasks
            else:
                coverage = 0.0
            display('Coverage   : %.0f%% (%d of %d tasks are tested)' % (coverage, self.num_tested_tasks, self.num_changed_tasks))

            if self.num_tested_tasks < self.num_changed_tasks:
                display('Not covered:')
                for task_name in self.not_tested_tasks:
                    display(' - %s' % (task_name))

            if self.num_failed_tests != 0:
                display('')
                display('WARNING: serverspec still detects %d failures' % (self.num_failed_tests))

            display('*** Kirby End *******')
