
from mock import patch
import unittest

from kirby.setting_manager import SettingManager

import utils


class SettingManagerTest(unittest.TestCase):
    def setUp(self):
        utils.reset_kirby_env_vars()

    def test_init_use_setting_file(self):
        setting_manager = SettingManager('./sample.conf')
        self.assertEqual(setting_manager.enable_kirby, True)
        self.assertEqual(setting_manager.serverspec_dir, '/opt')
        self.assertEqual(setting_manager.serverspec_cmd, 'rake spec')

    def test_init_use_invalid_setting_file(self):
        setting_manager = SettingManager('./sample_invalid.conf')
        self.assertEqual(setting_manager.enable_kirby, False)
        self.assertIsNone(setting_manager.serverspec_dir, None)
        self.assertIsNone(setting_manager.serverspec_cmd, None)

    def test_init_use_no_setting_file(self):
        setting_manager = SettingManager()
        self.assertEqual(setting_manager.enable_kirby, False)
        self.assertIsNone(setting_manager.serverspec_dir, None)
        self.assertIsNone(setting_manager.serverspec_cmd, None)

    @patch.dict('os.environ',
                {'KIRBY_ENABLE': 'no', 'KIRBY_SERVERSPEC_DIR': 'env_var1', 'KIRBY_SERVERSPEC_CMD': 'env_var2'})
    def test_init_use_envvar(self):
        setting_manager = SettingManager('./sample.conf')
        self.assertEqual(setting_manager.enable_kirby, False)
        self.assertEqual(setting_manager.serverspec_dir, 'env_var1')
        self.assertEqual(setting_manager.serverspec_cmd, 'env_var2')
