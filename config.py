#!/usr/bin/env python
# -*- encoding=utf8 -*-
import configparser
import os


class Config(object):
    def __init__(self, config_file='./config.ini'):
        self._path = os.path.join(os.getcwd(), config_file)
        if not os.path.exists(self._path):
            raise FileNotFoundError("No such file: config.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding='utf-8-sig')
        self._configRaw = configparser.RawConfigParser()
        self._configRaw.read(self._path, encoding='utf-8-sig')

    def get(self, section, name):
        return self._config.get(section, name)

    def getRaw(self, section, name):
        if self._configRaw.has_option(section, name):
            return self._configRaw.get(section, name)
        else:
            return ''


global_config = Config()
