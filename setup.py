from setuptools import setup, find_packages

setup(
    name='kluge_web',
    version='1.0',
    packages=find_packages(exclude=['tests']),
    test_suite="tests",
    install_requires=['redis', 'Flask', 'Flask-Testing', 'Flask-RESTful']
)