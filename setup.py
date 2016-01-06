#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='helpers',
      version='0.2',
      description='My little helpers',
      url='https://github.com/watercrossing/helpers',
      license='MIT',
      author='Ingolf Becker',
      author_email='ingolf.becker@googlemail.com',
      packages=find_packages(),
      install_requires = ['IPython', 'lxml', 'dill', 'scipy', 'matplotlib', ],
      classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2',
            'Topic :: Software Development :: Libraries',
            'Topic :: Communications :: Typesetting :: LaTeX'
            ]
     )

