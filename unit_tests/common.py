# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This file is part of Katnip.
#
# Katnip is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Katnip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Katnip.  If not, see <http://www.gnu.org/licenses/>.
'''
Common functions / classes for unit tests
'''

import unittest
import logging
from kitty.model import Template


test_logger = None


def get_test_logger(module_name):
    global test_logger
    if test_logger is None:
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] -> %(message)s'
        )
        handler = logging.FileHandler('logs/%s.log' % module_name, mode='w')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        test_logger = logger
    return test_logger


def warp_with_template(fields):
    '''
    wrap a lego with template
    '''
    return Template(name='uut template', fields=fields)


def get_mutation_set(t, reset=True):
    '''
    return a list of all mutations for the template
    '''
    res = set([])
    res.add(t.render().bytes)
    while t.mutate():
        res.add(t.render().bytes)
    if reset:
        t.reset()
    return res


def metaTest(func):
    def test_wrap(self):
        if self.__class__.__meta__:
            self.skipTest('Test should not run from meta class')
        else:
            return func(self)
    return test_wrap


class BaseTestCase(unittest.TestCase):
    def setUp(self, field_class=None):
        self.logger = get_test_logger(type(self).__module__)
        self.logger.info('TESTING METHOD: %s', self._testMethodName)
        self.todo = []
        self.cls = field_class

    def get_all_mutations(self, field, reset=True):
        res = []
        while field.mutate():
            rendered = field.render()
            res.append(rendered)
            self.logger.debug(rendered.tobytes().encode('hex'))
        if reset:
            field.reset()
        return res
