from setuptools import setup, find_packages
import os

version = '0.8'

setup(name='ilo.customizations',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Khairil Yusof',
      author_email='kaeru.my',
      url='https://svn.dev.inigo-tech.com/ilo/ilo.customizations',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ilo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.jbot'
          # -*- Extra requirements: -*-
      ]
      )
