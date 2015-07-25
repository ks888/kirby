
import ansible.utils  # unused, but necessary to avoid circular imports
from ansible.callbacks import display
import ConfigParser
import os
import re
import subprocess

version = '0.0.1'


class CallbackModule(object):
    """Plugin for analyzing task coverage"""

    def __init__(self):
        config_file = os.environ.get('KIRBY_CONFIG', None)
        if config_file is None:
            config_file = os.getcwd() + '/kirby.cfg'

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

            if result is None:
                display('[kirby] serverspec\'s result is unexpected...disable kirby', stderr=True)
                self.setting_manager.enable_kirby = False
                return

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
            if 'changed' in res and res['changed']:
                result = self.runner.run()
                prev_num_failed_tests = self.num_failed_tests
                self.num_tests = result[0]
                self.num_failed_tests = result[1]

                if 'coverage_skip' in self.curr_task_name:
                    return

                self.num_changed_tasks += 1
                if self.num_failed_tests < prev_num_failed_tests:
                    self.num_tested_tasks += 1
                else:
                    self.not_tested_tasks += [self.curr_task_name]

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


class SettingManager(object):
    def __init__(self, setting_file=None):
        self.parser = ConfigParser.SafeConfigParser()
        if setting_file is not None:
            self.parser.read(setting_file)

        self.enable_kirby = self._mk_boolean(self._get_config('defaults', 'enable_kirby', 'KIRBY_ENABLE', 'false'))
        self.serverspec_dir = self._get_config('defaults', 'serverspec_dir', 'KIRBY_SERVERSPEC_DIR', None)
        self.serverspec_cmd = self._get_config('defaults', 'serverspec_cmd', 'KIRBY_SERVERSPEC_CMD', None)

    def _get_config(self, section, option, env_var, default):
        value = os.environ.get(env_var, None)
        if value is not None:
            return value

        try:
            value = self.parser.get(section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            # use default value
            pass
        if value is not None:
            return value

        return default

    def _mk_boolean(self, value):
        if value is None:
            return False

        val = str(value)
        if val.lower() in ["true", "t", "y", "1", "yes"]:
            return True
        else:
            return False


class ServerspecRunner(object):
    """Run serverspec command and retrieve its results"""
    pattern = re.compile(r'(\d+) examples?, (\d+) failures?')

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
        if match_result is None:
            return None

        num_test = int(match_result.group(1))
        num_failed_test = int(match_result.group(2))

        return (num_test, num_failed_test)
