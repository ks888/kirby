
import ConfigParser
import os


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
