#! /bin/python

from setuptools import setup

with open('README.md') as readme:
    long_desc = readme.read()

setup(
    name='redditshelf',
    version='0.1.2',
    description='A CLI to organize reddit ebooks',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url='https://github.com/PhictionalOne/redditshelf.git',
    author='Alexander Phi. Goetz',
    author_email='code@phictional.de',
    py_modules=['redditshelf,py'],
    install_requires=[
        'Click',
        'Pathlib'
    ],
    entry_points='''
        [console_scripts]
        redditshelf=redditshelf:cli
    ''',
    # from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Utilities"
    ],
)