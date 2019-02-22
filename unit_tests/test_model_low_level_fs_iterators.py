# Copyright (C) 2019 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
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
Tests for FS iterator fields
'''
from common import BaseTestCase
from katnip.model.low_level.fs_iterators import FsContent, FsNames
from pyfakefs.fake_filesystem_unittest import Patcher
import six


class FsNamesTests(BaseTestCase):

    __meta__ = False

    def setUp(self, cls=FsNames):
        super(FsNamesTests, self).setUp(cls)
        self.base_dir = '/testdir'
        self._default_uut_kwargs = {
            'path': self.base_dir, 'name_filter': '*', 'recurse': True, 'full_path': True, 'include_dirs': True
        }

    def genericTest(self, uut_kwargs, ffs_config, expected):
        with Patcher() as patcher:
            # set up file system
            for c in ffs_config:
                patcher.fs.create_file(file_path='%s/%s' % (self.base_dir, c[0]), contents=c[1])
            # now set up field (enumeration done at construction
            for k, v in self._default_uut_kwargs.items():
                uut_kwargs.setdefault(k, v)
            uut = FsNames(**uut_kwargs)

            # check results
            mutations = set([m.tobytes() for m in self.get_all_mutations(uut)])
            if six.PY3:
                expected = [e.encode() for e in expected]
            expected = set(expected)
            self.assertEqual(expected, mutations)

            # check after reset again
            mutations = set([m.tobytes() for m in self.get_all_mutations(uut)])
            self.assertEqual(expected, mutations)

    def testRecurseIncludeDirsFullPathSingleFile(self):
        uut_kargs = {}
        ffs_config = [
            ['f1', 'content1']
        ]
        expected = ['%s/f1' % self.base_dir]
        self.genericTest(uut_kargs, ffs_config, expected)

    def testRecurseIncludeDirsFullPathMultiFile(self):
        uut_kargs = {}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
        ]
        expected = ['%s/%s' % (self.base_dir, c[0]) for c in ffs_config]
        self.genericTest(uut_kargs, ffs_config, expected)

    def testRecurseIncludeDirsFullPathMultiFileWithDirs(self):
        uut_kargs = {'recurse': True}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
            ['in1/f3', 'content3'],
        ]
        expected = ['%s/%s' % (self.base_dir, c[0]) for c in ffs_config]
        expected.append('%s/in1' % self.base_dir)
        self.genericTest(uut_kargs, ffs_config, expected)

    def testRecurseIncludeDirsFullPathMultiFileWithDirsAndDepth(self):
        uut_kargs = {'recurse': True}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
            ['in1/f3', 'content3'],
            ['in2/f4', 'content4'],
            ['in2/in3/f5', 'content5'],
        ]
        expected = ['f1', 'f2', 'in1', 'in2', 'in1/f3', 'in2/f4', 'in2/in3', 'in2/in3/f5']
        expected = ['%s/%s' % (self.base_dir, f) for f in expected]
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNoRecurseIncludeDirsFullPathMultiFileWithDirsAndDepth(self):
        uut_kargs = {'recurse': False}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
            ['in1/f3', 'content3'],
            ['in2/f4', 'content4'],
            ['in2/in3/f5', 'content5'],
        ]
        expected = ['f1', 'f2', 'in1', 'in2']
        expected = ['%s/%s' % (self.base_dir, f) for f in expected]
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNoRecurseNoIncludeDirsFullPathMultiFileWithDirsAndDepth(self):
        uut_kargs = {'recurse': False, 'include_dirs': False}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
            ['in1/f3', 'content3'],
            ['in2/f4', 'content4'],
            ['in2/in1/f5', 'content5'],
        ]
        expected = ['f1', 'f2']
        expected = ['%s/%s' % (self.base_dir, f) for f in expected]
        self.genericTest(uut_kargs, ffs_config, expected)

    def testRecurseIncludeDirsNoFullPathMultiFileWithDirsAndDepth(self):
        uut_kargs = {'recurse': True, 'full_path': False}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
            ['in1/f3', 'content3'],
            ['in2/f4', 'content4'],
            ['in2/in3/f5', 'content5'],
        ]
        expected = ['f1', 'f2', 'f3', 'f4', 'f5', 'in1', 'in2', 'in3']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNameFilter(self):
        uut_kargs = {'name_filter': '*.test'}
        ffs_config = [
            ['f1', 'should_not_happen1'],
            ['f2.test', 'content2']
        ]
        expected = ['f2']
        expected = ['%s/%s.test' % (self.base_dir, e) for e in expected]
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNameFilterRecurse(self):
        uut_kargs = {'name_filter': '*.test'}
        ffs_config = [
            ['f1', 'should not happen 1'],
            ['f2.test', 'content2'],
            ['in1/f3', 'should not happen 3'],
            ['in1/f4.test', 'content4'],
        ]
        expected = ['f2', 'in1/f4']
        expected = ['%s/%s.test' % (self.base_dir, e) for e in expected]
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNameFilterRecurseDirs(self):
        uut_kargs = {'name_filter': '*.test', 'recurse': True}
        ffs_config = [
            ['f1', 'should not happen 1'],
            ['f2.test', 'content2'],
            ['in1/f3', 'should not happen 3'],
            ['in1/f4.test', 'content4'],
            ['in2.test/f5', 'should not happen 5'],
        ]
        expected = ['f2', 'in1/f4', 'in2']
        expected = ['%s/%s.test' % (self.base_dir, e) for e in expected]
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNameFilterNoRecurseDirs(self):
        uut_kargs = {'name_filter': '*.test', 'recurse': False}
        ffs_config = [
            ['f1', 'should not happen 1'],
            ['f2.test', 'content2'],
            ['in1/f3', 'should not happen 3'],
            ['in1/f4.test', 'content4'],
            ['in2.test/f5', 'should not happen 5'],
        ]
        expected = ['f2', 'in2']
        expected = ['%s/%s.test' % (self.base_dir, e) for e in expected]
        self.genericTest(uut_kargs, ffs_config, expected)


class FsContentTests(BaseTestCase):

    __meta__ = False

    def setUp(self, cls=FsContent):
        super(FsContentTests, self).setUp(cls)
        self.base_dir = '/testdir'
        self._default_uut_kwargs = {
            'path': self.base_dir, 'name_filter': '*', 'recurse': True,
        }

    def genericTest(self, uut_kwargs, ffs_config, expected):
        with Patcher() as patcher:
            # set up file system
            for c in ffs_config:
                patcher.fs.create_file(file_path='%s/%s' % (self.base_dir, c[0]), contents=c[1])
            # now set up field (enumeration done at construction
            for k, v in self._default_uut_kwargs.items():
                uut_kwargs.setdefault(k, v)
            uut = self.cls(**uut_kwargs)

            # check results
            mutations = set([m.tobytes() for m in self.get_all_mutations(uut)])
            if six.PY3:
                expected = [e.encode() for e in expected]
            expected = set(expected)
            self.assertEqual(expected, mutations)

            # check after reset again
            mutations = set([m.tobytes() for m in self.get_all_mutations(uut)])
            self.assertEqual(expected, mutations)

    def testRecurseSingleFile(self):
        uut_kargs = {}
        ffs_config = [
            ['f1', 'content1']
        ]
        expected = ['content1']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testRecurseMultiFile(self):
        uut_kargs = {}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
        ]
        expected = ['content1', 'content2']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testRecurseMultiFileWithDirs(self):
        uut_kargs = {'recurse': True}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
            ['in1/f3', 'content3'],
        ]
        expected = ['content1', 'content2', 'content3']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testRecurseMultiFileWithDirsAndDepth(self):
        uut_kargs = {'recurse': True}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
            ['in1/f3', 'content3'],
            ['in2/f4', 'content4'],
            ['in2/in3/f5', 'content5'],
        ]
        expected = ['content1', 'content2', 'content3', 'content4', 'content5']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNoRecurseMultiFileWithDirsAndDepth(self):
        uut_kargs = {'recurse': False}
        ffs_config = [
            ['f1', 'content1'],
            ['f2', 'content2'],
            ['in1/f3', 'content3'],
            ['in2/f4', 'content4'],
            ['in2/in3/f5', 'content5'],
        ]
        expected = ['content1', 'content2']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNameFilter(self):
        uut_kargs = {'name_filter': '*.test'}
        ffs_config = [
            ['f1', 'should_not_happen1'],
            ['f2.test', 'content2']
        ]
        expected = ['content2']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNameFilterRecurse(self):
        uut_kargs = {'name_filter': '*.test'}
        ffs_config = [
            ['f1', 'should not happen 1'],
            ['f2.test', 'content2'],
            ['in1/f3', 'should not happen 3'],
            ['in1/f4.test', 'content4'],
        ]
        expected = ['content2', 'content4']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNameFilterRecurseDirs(self):
        uut_kargs = {'name_filter': '*.test', 'recurse': True}
        ffs_config = [
            ['f1', 'should not happen 1'],
            ['f2.test', 'content2'],
            ['in1/f3', 'should not happen 3'],
            ['in1/f4.test', 'content4'],
            ['in2.test/f5', 'should not happen 5'],
        ]
        expected = ['content2', 'content4']
        self.genericTest(uut_kargs, ffs_config, expected)

    def testNameFilterNoRecurseDirs(self):
        uut_kargs = {'name_filter': '*.test', 'recurse': False}
        ffs_config = [
            ['f1', 'should not happen 1'],
            ['f2.test', 'content2'],
            ['in1/f3', 'should not happen 3'],
            ['in1/f4.test', 'content4'],
            ['in2.test/f5', 'should not happen 5'],
        ]
        expected = ['content2']
        self.genericTest(uut_kargs, ffs_config, expected)
