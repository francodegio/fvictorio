from setuptools import setup, find_packages

setup(
    name='fvictorio',
    description='A package for processing fvictorio data.',
    packages=find_packages(where='src'),
    package_dir={'':'src'},
)