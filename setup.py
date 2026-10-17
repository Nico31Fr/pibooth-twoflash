#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import open
import os.path as osp
from setuptools import setup


HERE = osp.abspath(osp.dirname(__file__))

# Keep packaging metadata independent from the runtime plugin. Importing the
# plugin here would require hardware dependencies before pip can install them.
PACKAGE_NAME = 'pibooth-twoflash'
PACKAGE_VERSION = '1.2.0'
PACKAGE_DESCRIPTION = 'A pibooth plugin to control warm and cool white LED strips.'


def main():
    setup(
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        description=PACKAGE_DESCRIPTION,
        long_description=open(osp.join(HERE, 'README.md'), encoding='utf-8').read(),
        long_description_content_type='text/markdown',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Natural Language :: English',
            'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        ],
        author="Grena",
        url="https://github.com/Nico31Fr/pibooth-twoflash",
        download_url="https://github.com/Nico31Fr/pibooth-twoflash/archive/{}.tar.gz".format(PACKAGE_VERSION),
        license='MIT license',
        platforms=['unix', 'linux'],
        keywords=[
            'Raspberry Pi',
            'camera',
            'photobooth',
            'led'
        ],
        py_modules=['pibooth_twoflash'],
        install_requires=[
            'pibooth>=2.0.0',
            'gpiozero>=1.6'
        ],
        zip_safe=False,  # Don't install the lib as an .egg zipfile
        entry_points={'pibooth': ["pibooth_twoflash = pibooth_twoflash"]},
    )


if __name__ == '__main__':
    main()
