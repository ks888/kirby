#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.abspath('lib'))
from setuptools import setup, find_packages

from kirby import __version__

setup(
    name='kirby',
    version=__version__,
    packages=find_packages('lib'),
    package_dir={'kirby': 'lib/kirby'},
)
