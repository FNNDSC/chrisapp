from os import path
from setuptools import setup

with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'chrisapp',
    version          = '1.1.7',
    description      = 'Superclass for Chris plugin apps',
    long_description = readme,
    author           = 'FNNDSC',
    author_email     = 'dev@babymri.org',
    url              = 'https://github.com/FNNDSC/chrisapp',
    packages         = ['chrisapp'],
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires='>=3.5'
)
