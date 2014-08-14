#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='helpers',
      version='0.01',
      description='My little helpers',
      author='Ingolf Becker',
      author_email='ingolf.becker@googlemail.com',
      packages=find_packages(),
      install_requires = ['IPython', 'lxml', 'dill', 'scipy', 'matplotlib', ]
     )

