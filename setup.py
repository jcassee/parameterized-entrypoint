import os
from subprocess import check_call, Popen

from setuptools import setup, find_packages
from distutils.command.build import build


class build_pyinstaller(build):
    def run(self):
        build.run(self)

        from PyInstaller.__main__ import run
        run(['-F', 'entrypoint.py'])


class build_docker_alpine(build):
    def run(self):
        build.run(self)

        check_call(['docker', 'build', '-t', 'build-alpine',
                '-f', 'Dockerfile.build-alpine', '.'])
        # Create as executable file
        mode = (os.O_WRONLY | os.O_TRUNC | os.O_CREAT)
        with os.fdopen(os.open('dist/entrypoint-alpine', mode)) as output:
            Popen(['docker', 'run', '--rm', 'build-alpine',
                    'cat', 'dist/entrypoint'], stdout=output)


setup(
    name='parameterized-entrypoint',
    version='0.10.0',
    author='Joost Cassee',
    author_email='joost@cassee.net',

    url='https://github.com/jcassee/parameterized-entrypoint',
    license='MIT',
    description='Docker entrypoint that processes template files.',
    keywords=['Jinja2', 'templating', 'Docker'],

    cmdclass={
        'build': build_pyinstaller,
        'build_alpine': build_docker_alpine,
    },

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
