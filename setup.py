#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
import os
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
import subprocess

import distutils.cmd
import distutils.log
from setuptools import find_packages
from setuptools import setup
import setuptools.command.build_py

def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


def requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip()]

class PyinstallerCommand(distutils.cmd.Command):
    """A custom command to run pyinstaller"""

    description = 'run pyinstaller to create all-in-one executable'
    user_options = [
        # The format is (long option, short option, description).
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        command = ['pyinstaller', os.path.join("src","lbry_channel_mirror","main.py"),
                   "--clean", "-F", "-n", "lbry_channel_mirror"]
        self.announce(
            'Running command: %s' % str(command),
            level=distutils.log.INFO)
        subprocess.check_call(command)


class BuildPyCommand(setuptools.command.build_py.build_py):
    """Custom build command."""
    def run(self):
        # Do whatever here
        setuptools.command.build_py.build_py.run(self)

setup(
    name='lbry_channel_mirror',
    version='0.1.0',
    cmdclass={
        'build_exe': PyinstallerCommand,
        'build_py': BuildPyCommand
    },
    license='MIT',
    description='Tool to synchronize files from a lbry channel to a local directory',
    author='EnigmaCurry',
    url='https://github.com/EnigmaCurry/lbry-channel-mirror',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    install_requires=requirements(),
    entry_points={
        'console_scripts': [
            'lbry_channel_mirror = lbry_channel_mirror.main:main',
        ]
    },
)
