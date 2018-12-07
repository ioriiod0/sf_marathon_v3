# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-01 14:40:43
# @Last modified by:   ioriiod0
# @Last modified time: 2017-12-05T16:30:19+08:00


import sys
from setuptools import setup, find_packages

__title__ = 'marathon'
__author__ = 'gao lei'
__email__ = 'ioriiod0@gmail.com'
__version__ = '0.0.1'

setup(name=__title__,
        version=__version__,
        author=__author__,
        author_email=__email__,
        install_requires=[
        ],
        package_dir={'': 'lib'},
        packages=find_packages('lib'),
        cmdclass={},
        zip_safe=False
        )
