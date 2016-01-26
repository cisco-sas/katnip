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

import os
import time
import datetime

from kitty.monitors.base import BaseMonitor

import paramiko


class SshFileMonitor(BaseMonitor):
    '''
    SshFileMonitor monitors for files using a file_mask.
    If found - moves files to local folder, renaming with test number.
    '''

    def __init__(self, name, username, password, hostname, port, 
                 file_mask,
                 local_dir,
                 fail_if_exists=True,
                 setup_commands = [],
                 on_fail_command=None,
                 on_fail_delay=0,
                 logger=None):
        '''
        :param name: name of the object
        :param username: ssh login username
        :param password: ssh login password
        :param hostname: ssh server ip
        :param port: ssh server port
        :param file_mask: file_mask to fetch
        :param local_dir: local_path to store fetched files
        :param fail_if_exists: fail test if file exists (default: True)
        :param logger: logger for this object (default: None)
        '''
        super(SshFileMonitor, self).__init__(name, logger)

        self._username = username
        self._password = password
        self._hostname = hostname
        self._port = port
        self._file_mask = file_mask
        self._local_dir = local_dir
        self._fail_if_exists = fail_if_exists
        self._setup_commands = setup_commands
        self._on_fail_command = on_fail_command
        self._on_fail_delay = on_fail_delay
        self._ssh = None

    def _ssh_command(self, cmd):
        return_code = None
        try:
            self._connect_ssh()
            (self._stdin, self._stdout, self._stderr) = self._ssh.exec_command(cmd)
            return_code = self._stdout.channel.recv_exit_status()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.logger.debug('SSHFileMonitor: ssh command exec error: %s' % str(e))
        return return_code

    def setup(self):
        '''
        Called at the begining of the fuzzing session
        '''
        super(SshFileMonitor, self).setup()
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        self._local_dir = os.path.join(self._local_dir, timestamp)
        os.makedirs(self._local_dir)

        self._connect_ssh()

        for command in self._setup_commands:
            self.logger.debug('running remote setup command: %s' % command)
            res = self._ssh_command(command)
            if res != 0:
                self.logger.debug('Error running command: %s. got %s' % (command, res))
                self.logger.debug('stdout: %s' % self._stdout.read())
                self.logger.debug('stderr: %s' % self._stderr.read())

    def teardown(self):
        if self._ssh:
            self._ssh.close()
        self._ssh = None
        super(SshFileMonitor, self).teardown()

    def _connect_ssh(self):
        if not self._ssh:
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(self._hostname, self._port, self._username, self._password)

    def post_test(self):
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(self._hostname, self._port, self._username, self._password)

        cmd = 'ls %s' % self._file_mask
        (self._stdin, self._stdout, self._stderr) = self._ssh.exec_command(cmd)
        return_code = self._stdout.channel.recv_exit_status()
        self.report.add('file_mask', self._file_mask)
        if return_code != 0:
            self.report.add('status', 'No files found')
        else:
            ls_stdout = self._stdout.read()
            ls_stderr = self._stderr.read()
            del ls_stderr
            self.report.add('failed', True)
            self.report.add('remote core_file', ls_stdout.strip())
            remote_path = ls_stdout.strip()
            local_path = os.path.join(self._local_dir, 'test_%05d' % self.test_number)
            sftp = self._ssh.open_sftp()
            sftp.get(str(remote_path), str(local_path))
            sftp.remove(remote_path)
            sftp.close()
            self.report.add('local core_file', local_path)
            if self._on_fail_command:
                self.logger.info('running remote on fail command: %s', self._on_fail_command)
                self.report.add('on_fail_command', self._on_fail_command)
                self.report.add('on_fail_delay', self._on_fail_delay)
                self._ssh_command(self._on_fail_command)
                time.sleep(self.on_fail_delay)

        super(SshFileMonitor, self).post_test()

    def X_pre_test(self, test_number):
        super(SshFileMonitor, self).pre_test(test_number)

    def _monitor_func(self):
        '''
        Nothing is done here, so we use a sleep for now.
        '''
        time.sleep(0.1)
