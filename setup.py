#!/usr/bin/env python
import os
from setuptools import setup
from setuptools.command.install import install

from synchronization import __version__ as version, __author__ as author, __email__ as email


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        os.system('systemctl daemon-reload')


setup(
    name='synchronization',
    version=version,
    description='Synchronization for Beaker tasks',
    author=author,
    author_email=email,
    include_package_data=True,
    packages=[
        'synchronization',
        'synchronization.client',
        'synchronization.server',
    ],
    entry_points={
        'console_scripts': [
            'sync_client = synchronization.client.__main__:main',
            'sync_server = synchronization.server.__main__:main',
        ],
    },
    data_files=[
        (
            '/usr/lib/systemd/system', [
                'synchronization.service',
            ]
        ),
    ],
    cmdclass={
      'install': PostInstallCommand,
    },
)
