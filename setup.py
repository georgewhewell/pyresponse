import sys

from distutils.core import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    pytest_args = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='pyresponse',
    version='1.2.7', 
    packages=['pyresponse', 'pyresponse.lib'],
    install_requires=['suds-jurko', 'pytz'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
