import unittest
import os.path

class TestCodeFormat(unittest.TestCase):
    def test_flake8_conformance(self):
        # Unfortunately, the module ignores the config file so we have to use the shell
        # flake8 settings are in tox.ini
        cmd = 'flake8'
        result = os.system(cmd)
        self.assertEquals(result, 0, "Found code style errors (and warnings).")
