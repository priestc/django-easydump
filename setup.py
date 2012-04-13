#!/usr/bin/env python
from setuptools import setup, find_packages

METADATA = dict(
    name='django-easydump',
    version='0.2.1',
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    description='Easily load database snapshots across deployments',
    long_description=open('README.md').read(),
    url='http://priestc.github.com/django-easydump/',
    keywords='django dump database',
    install_requires=['django', 'python-dateutil', 'boto'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=find_packages(),
)

if __name__ == '__main__':
    setup(**METADATA)
