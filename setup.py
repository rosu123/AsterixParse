#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 17:26:37 2024

@author: rodrigo
"""

"""AsterixParse module setup"""


import json
from os import path
from setuptools import setup, find_packages
from sys import version_info
import pathlib

here = pathlib.Path(__file__).parent.resolve()

VERSION = "0.1.0"
CURR_PATH = "{}{}".format(path.abspath(path.dirname(__file__)), '/')

long_description = (here / "README.md").read_text(encoding="utf-8")


def path_format(file_path=None, file_name=None, is_abspath=False,
                ignore_raises=False):
    """
    Get path joined checking before if path and filepath exist,
     if not, raise an Exception
     if ignore_raise it's enabled, then file_path must include '/' at end lane
    """
    path_formatted = "{}{}".format(file_path, file_name)
    if ignore_raises:
        return path_formatted
    if file_path is None or not path.exists(file_path):
        raise IOError("Path '{}' doesn't exists".format(file_path))
    if file_name is None or not path.exists(path_formatted):
        raise IOError(
            "File '{}{}' doesn't exists".format(file_path, file_name))
    if is_abspath:
        return path.abspath(path.join(file_path, file_name))
    else:
        return path.join(file_path, file_name)


def read_file(is_json=False, file_path=None, encoding='utf-8',
              is_encoding=True, ignore_raises=False):
    """Returns file object from file_path,
       compatible with all py versiones
    optionals:
      can be use to return dict from json path
      can modify encoding used to obtain file
    """
    text = None
    try:
        if file_path is None:
            raise Exception("File path received it's None")
        if version_info.major >= 3:
            if not is_encoding:
                encoding = None
            with open(file_path, encoding=encoding) as buff:
                text = buff.read()
        if version_info.major <= 2:
            with open(file_path) as buff:
                if is_encoding:
                    text = buff.read().decode(encoding)
                else:
                    text = buff.read()
        if is_json:
            return json.loads(text)
    except Exception as err:
        if not ignore_raises:
            raise Exception(err)
    return text


def read(file_name=None, is_encoding=True, ignore_raises=False):
    """Read file"""
    if file_name is None:
        raise Exception("File name not provided")
    if ignore_raises:
        try:
            return read_file(
                is_encoding=is_encoding,
                file_path=path_format(
                    file_path=CURR_PATH,
                    file_name=file_name,
                    ignore_raises=ignore_raises))
        except Exception:
            # TODO: not silence like this,
            # must be on setup.cfg, README path
            return 'NOTFOUND'
    return read_file(is_encoding=is_encoding,
                     file_path=path_format(
                         file_path=CURR_PATH,
                         file_name=file_name,
                         ignore_raises=ignore_raises))


setup(
    name='asterixparse',
    version=VERSION,
    description='Python project to Decode EUROCONTROL ASTERIX data format messages',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=read("LICENSE", is_encoding=False, ignore_raises=True),
    #url='https://test.com',
    #download_url='https://test.tar'.format(VERSION),
    author='Rodrigo Perela',
    author_email='rosu.perela@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['AsterixParse', 'ASTERIX', 'EUROCONTROL','development', 'ModeS', 
              'BDS', 'Category21', 'Category48', 'ADS-B'],
    
    #package_dir={"": "AsterixParse"},
    packages=find_packages(),
    python_requires=">=3.6, <4",
    project_urls={
        "Bug Reports": "https://github.com/rosu123/AsterixParse/issues",
        "Source": "https://github.com/rosu123/AsterixParse",
    },
    install_requires=['datetime', 'dataclasses',
                      'typing', 'pandas', 'jsonpickle', 
                      'pymongo', 'tqdm'],
)