from setuptools import setup, find_packages
import os

VERSION = '0.2.4'
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
    install_requires=['kittyfuzzer'],
    keywords='fuzz,fuzzing,framework,sulley,kitty,katnip',
    package_data={},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Utilities'
    ]
)
