import os

from setuptools import setup, find_packages
from distutils.command.build import build


class pyinstaller_build(build):
    def run(self):
        build.run(self)

        from PyInstaller.__main__ import run
        run(['-F', 'entrypoint.py'])


setup(
    name='parameterized-entrypoint',
    version='0.7.0',
    author='Joost Cassee',
    author_email='joost@cassee.net',

    url='https://github.com/jcassee/parameterized-entrypoint',
    license='MIT',
    description='Docker entrypoint that processes template files.',
    keywords=['Jinja2', 'templating', 'Docker'],

    cmdclass={'build': pyinstaller_build},

    py_modules=['entrypoint'],
    entry_points={
        'console_scripts': [
            'entrypoint = entrypoint:main',
        ]
    },

    install_requires=[
      'Jinja2',
    ],

    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
