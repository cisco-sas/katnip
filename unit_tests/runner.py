#!/usr/bin/env python
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

import unittest
import os
import sys
import inspect

module_dir = 'katnip'
currentdir = os.path.dirname(
    os.path.abspath(
        inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Test files to use
from lego_json import *
from lego_url import *
from lego_dynamic import *
from model_low_level_encoders import *
from test_model_low_level_scapy_field import *


if __name__ == '__main__':
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    unittest.main(verbosity=10)
