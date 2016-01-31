from setuptools import setup, find_packages
import os

VERSION = '0.2.1'
AUTHOR = 'Cisco SAS team'
EMAIL = 'kitty-fuzzer@googlegroups.com'
URL = 'https://github.com/cisco-sas/katnip.git'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='katnip',
    version=VERSION,
    description='Extensions for the Kitty fuzzing framework',
    long_description=read('README.rst'),
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(),
    install_requires=[],
    keywords='fuzz framework sulley kitty katnip',
    package_data={}
)
