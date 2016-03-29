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
import paramiko


class ReconnectingSSHConnection(object):
    """
    A wrapper around paramiko's SSHClient which handles connection dropouts gracefully.
    """
    def __init__(self, hostname, port, username, password):
        """
        :param hostname: ssh server hostname or ip
        :param port: ssh server port
        :param username: ssh login username
        :param password: ssh login password
        """
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password

        self._paramiko = paramiko.SSHClient()
        self._paramiko.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _ensure_connected(self):
        if self._paramiko.get_transport() is None or not self._paramiko.get_transport().isAlive():
            self._paramiko.connect(self._hostname, self._port, self._username, self._password)

    def exec_command(self, command):
        """
        Execute a command on the ssh server.

        :param command: the command string to execute
        :returns: a tuple of the return_code from the command, the stdout output and the stderr output
        """
        self._ensure_connected()
        stdin, stdout, stderr = self._paramiko.exec_command(command)
        return_code = stdout.channel.recv_exit_status()
        return return_code, stdout.read(), stderr.read()

    def close(self):
        """
        Close the connection
        """
        self._paramiko.close()

    def put(self, localpath, remotepath, callback=None, confirm=True):
        """
        Put a file on the ssh server using sftp.

        :param localpath: the local path to the file to copy
        :param remotepath: the remote path to which the file should be copied
        :param callback: optional callback function (form: func(int, int)) that accepts the bytes transferred so far and the total bytes to be transferred.
        :param confirm: whether to do a stat() on the file afterwards to confirm the file size
        """
        self._ensure_connected()
        return self.open_sftp().put(localpath, remotepath, callback, confirm)

    def get(self, remotepath, localpath, callback=None):
        """
        Get a file from the ssh server using sftp.

        :param remotepath: the remote path of the file to be copied
        :param localpath: the local path to which the file should be copied
        :param callback: optional callback function (form: func(int, int)) that accepts the bytes transferred so far and the total bytes to be transferred.
        """
        self._ensure_connected()
        return self.open_sftp().get(remotepath, localpath, callback)


