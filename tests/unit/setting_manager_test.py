
from mock import patch
from nose.plugins.attrib import attr
import unittest
import os
import sys

sys.path.append(os.getcwd() + '/../..')
from callback_plugins.kirby import SettingManager

import utils


class SettingManagerTest(unittest.TestCase):
    def setUp(self):
        utils.reset_kirby_env_vars()

    def testInit_UseNone_DefaultIsUsed(self):
        setting_manager = SettingManager()
        self.assertEqual(setting_manager.enable, False)
        self.assertIsNone(setting_manager.serverspec_dir, None)
        self.assertIsNone(setting_manager.serverspec_cmd, None)

    def testInit_UseSettingFile_SettingFileIsUsed(self):
        setting_manager = SettingManager('./kirby.cfg')
        self.assertEqual(setting_manager.enable, True)
        self.assertEqual(setting_manager.serverspec_dir, '/opt')
        self.assertEqual(setting_manager.serverspec_cmd, 'rake spec')

    @patch.dict('os.environ',
                {'KIRBY_ENABLE': 'no', 'KIRBY_SERVERSPEC_DIR': 'env_var1', 'KIRBY_SERVERSPEC_CMD': 'env_var2'})
    def testInit_UseEnvVarAndSettingFile_EnvVarIsUsed(self):
        setting_manager = SettingManager('./kirby.cfg')
        self.assertEqual(setting_manager.enable, False)
        self.assertEqual(setting_manager.serverspec_dir, 'env_var1')
        self.assertEqual(setting_manager.serverspec_cmd, 'env_var2')

    def testInit_UseNonExistSettingFile_DefaultIsUsed(self):
        setting_manager = SettingManager('notfound.cfg')
        self.assertEqual(setting_manager.enable, False)
        self.assertIsNone(setting_manager.serverspec_dir, None)
        self.assertIsNone(setting_manager.serverspec_cmd, None)

    def testInit_UseInsufficientSettingFile_PartiallyUseDefault(self):
        setting_manager = SettingManager('kirby_insufficient.cfg')
        self.assertEqual(setting_manager.enable, True)  # file
        self.assertEqual(setting_manager.serverspec_dir, '/opt')  # file
        self.assertIsNone(setting_manager.serverspec_cmd, None)  # default
