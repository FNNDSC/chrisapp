from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'chrisapp',
    version          = '3.0.0',
    description      = 'Superclass for Chris plugin apps',
    long_description = readme,
    author           = 'FNNDSC',
    author_email     = 'dev@babymri.org',
    url              = 'https://github.com/FNNDSC/chrisapp',
    packages         = ['chrisapp'],
    install_requires = [
        'importlib-metadata; python_version<"3.8"'
    ],
    test_suite       = 'nose.collector',
    tests_require    = ['nose==1.3.7'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires = '>=3.6'
)
