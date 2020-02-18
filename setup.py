#!/usr/bin/env python3
import os
from setuptools import setup
from setuptools.command.install import install

from nepta.synchronization import __version__ as version, __author__ as author, __email__ as email


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        os.system('systemctl daemon-reload')


setup(
    name='nepta-synchronization',
    version=version,
    description='Synchronization for Beaker tasks',
    author=author,
    author_email=email,
    include_package_data=True,
    namespace_packages=['nepta'],
    packages=[
        'nepta.synchronization',
        'nepta.synchronization.client',
        'nepta.synchronization.server',
    ],
    entry_points={
        'console_scripts': [
            'sync_client = nepta.synchronization.client.__main__:main',
            'sync_server = nepta.synchronization.server.__main__:main',
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
