# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This module was authored and contributed by dark-lbp <jtrkid@gmail.com>
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

import time
import os
import threading
import traceback
import pykd
from kitty.core.threading_utils import FuncThread
from kitty.targets.server import ServerTarget


interesting_exception_codes = {
    0x80000001: "GUARD_PAGE_VIOLATION",
    0x80000005: "BUFFER_OVERFLOW",
    0xC0000005: "ACCESS_VIOLATION",
    0xC000001D: "ILLEGAL_INSTRUCTION",
    0xC0000144: "UNHANDLED_EXCEPTION",
    0xC0000409: "STACK_BUFFER_OVERRUN",
    0xC0000602: "UNKNOWN_EXCEPTION",
    0xC00000FD: "STACK_OVERFLOW",
    0XC000009D: "PRIVILEGED_INSTRUCTION",
}

break_in_exception_code = 0x80000003


class EventHandler(pykd.eventHandler):
    '''
    This class is used to Handler Event from PYKD, you can overwrite any methods which listed in
    this link(https://pykd.codeplex.com/wikipage?title=PYKD%200.3.%20API%20Reference#eventHandler)
    '''
    def __init__(self, target):
        '''
        :param target: Our PykdTarget
        '''
        super(EventHandler, self).__init__()
        self._target = target

    def onException(self, exceptionInfo):
        '''
        Triggered exception event. This example handler only recoder exception which we interested.

        :param exceptionInfo: Exception information
        :return: For ignore event method must return eventResult.noChange
        '''
        eip = pykd.reg('eip')
        last_exception = str(pykd.getLastException())
        exc_code = exceptionInfo.exceptionCode
        self._target.logger.info("Got Exception Code: %s at eip:%s" % (hex(exc_code), hex(eip)))
        if exc_code in interesting_exception_codes.keys():
            self._target.is_crash.set()
            self._target.crash_dump_finished.clear()
            self._target.report.failed("Got Exception Code: %s:%s at eip:%s" % (
                hex(exc_code), interesting_exception_codes[exc_code], hex(eip)))
            self._target.report.add("Error Code", "%s:%s" % (hex(exc_code), interesting_exception_codes[exc_code]))
            self._target.report.add("Last Event", "%s" % last_exception)
            self._target.report.add("Stacks", str(pykd.dbgCommand("k")))
            self._target.crash_dump_finished.set()
            return pykd.eventResult.Break
        elif exc_code == break_in_exception_code:
            # Handle break in event
            self._target.logger.info("Break in at eip:%s" % hex(eip))
            return pykd.eventResult.Break
        return pykd.eventResult.NoChange


class PykdTarget(ServerTarget):
    '''
    PykdTarget will run an application for each fuzzed payloads.
    To use PykdTarget your need install PYkd and Windbg first.
    Document link https://pykd.codeplex.com/documentation.
    '''

    def __init__(self, name, process_path, process_args=[], break_points=[], handler=None, logger=None, timeout=3):
        '''

        :param name: name of the object.
        :param process_path: path to the target executable.
        :param process_args: arguments to pass to the process.
        :param break_points: break points to set.
        :param handler: pykd event handler.
        :param logger: logger for this object (default: None)
        :param timeout: seconds to wait for the process before kill (default: 3)

        :example:

            ::

                PykdTarget(
                    name='PykdTarget',
                    process_path="/tmp/myApp",
                    process_args=['-a', '-c']
                    handler=MyEventHandler,
                    break_points=[],
                    timeout=2)

            Will run ``/tmp/myApp -a -c mutational_data`` using pykd for evey mutation with timeout of 2 seconds

        '''
        super(PykdTarget, self).__init__(name, logger)
        assert(process_path)
        assert(os.path.exists(process_path))
        self._process_path = process_path
        self._process_name = os.path.basename(process_path)
        self._process_args = process_args
        self.process_data = None
        self._break_points = break_points
        self._handler = handler
        self._timeout = timeout
        self._process = None
        self._pid = None
        self._system_pid = None
        self.is_crash = threading.Event()
        self.crash_dump_finished = threading.Event()

    def _get_exe_status(self):
        try:
            status = str(pykd.getExecutionStatus())
            return status
        except Exception as err:
            self.logger.debug("Can't get process execution status because of: %s" % err)
            return None

    def _wait_break(self, timeout=2):
        '''
        :param timeout: timeout in seconds. (default: 2)
        :return: True if Server is in break status, False otherwise
        '''
        end_time = time.time() + timeout
        delay = 0.0005  # 500 us -> initial delay of 1 ms
        while True:
            remaining = end_time - time.time()
            if remaining <= 0:
                return False
            time.sleep(delay)
            try:
                status = self._get_exe_status()
                if status == 'Break':
                    self.logger.debug('Process is in break status')
                    return True
            except Exception as err:
                self.logger.error("Received exception when wait process break: %s" % err)
                continue

    def _get_correct_process_id(self):
        while self._pid == 0xffffffff:
            try:
                self._pid = pykd.getCurrentProcessId()
            except Exception as err:
                self.logger.debug("Can't get correct process id because of: %s" % err)
                continue

    def _debug_server(self):
        '''
        debugger thread
        '''
        self._system_pid = None
        self.logger.info('Init pykd environment')
        pykd.initialize()
        try:
            # Start a new process for debugging
            argv = [self._process_path] + self._process_args + self.process_data
            argv = ' '.join(argv)
            self.logger.debug('Debugger starting server: %s' % argv)
            try:
                self.logger.info('Start running program with cmd:"%s"' % argv)
                self.report.add('cmd', argv)
                self._pid = pykd.startProcess(argv)
                self._get_correct_process_id()
                self.logger.debug('Process started. pykd_pid=%d' % self._pid)
                self._process = pykd.getCurrentProcess()
                self.logger.debug('Process is %s' % hex(self._process))
            except WindowsError:
                self.logger.error('debug_server received exception', traceback.fmt_exc())
            # Get Process System ID
            self._wait_break()
            while self._system_pid is None:
                try:
                    self._system_pid = pykd.getProcessSystemID(self._pid)
                    self.logger.info('process system_id=%d' % self._system_pid)
                except Exception as err:
                    self.logger.debug("Get system id fail because of: %s" % err)
                    continue
            # Set break points
            if self._wait_break():
                self.logger.info("Server is in break status setting break points")
                for bp in self._break_points:
                    pykd.setBp(bp)
                self.logger.info("Start register event handle")
                # This will register our handle
                handler = self._handler(self)
                self.logger.debug('Handler object is : %s' % handler)
                self.logger.info('Go !!!!!')
                pykd.go()
        except:
            self.logger.error('Got an exception in _debug_server')
            self.logger.error(traceback.format_exc())

    def _start_server_thread(self):
        '''
        start the server thread
        '''
        self._server_thread = FuncThread(self._debug_server)
        self._server_thread.start()

    def _kill_all_processes(self):
        '''
        kill all processes with the same name
        :return: True if all matching processes were killed properly, False otherwise
        '''
        if self._process:
            try:
                status = self._get_exe_status()
                self.logger.debug("Current status is %s start kill process" % status)
                if status == 'Break':
                    self.logger.info("Process is in break status, kill process now")
                    pykd.killAllProcesses()
                    self._pid = None
                    self._process = None
                else:
                    self.logger.info("Break in process, kill process now")
                    pykd.breakin()
                    self._wait_break()
                    # TODO: need find a way to replace time.sleep
                    time.sleep(0.05)
                    pykd.killAllProcesses()
                    self._pid = None
                    self._process = None
            except:
                self.logger.error('failed to kill process [%s]' % traceback.format_exc())
                return False
            return True

    def teardown(self):
        self._stop_process()
        self._pid = None
        self._process = None
        super(PykdTarget, self).teardown()

    def pre_test(self, test_number):
        super(PykdTarget, self).pre_test(test_number)
        self.is_crash.clear()
        self.crash_dump_finished.clear()
        self._stop_process()

    def post_test(self, test_num):
        if self.is_crash.wait(self._timeout):
            self.crash_dump_finished.wait(self._timeout)
        self._stop_process()
        # for each test case we need deinitialize the pykd, other wise event handle will not work.
        pykd.deinitialize()
        super(PykdTarget, self).post_test(test_num)

    def _send_to_target(self, payload):
        '''

        :param payload: payload to send (might be file path)
        '''
        self.logger.debug('send called')
        self.process_data = [payload]
        self._start_server_thread()

    def _stop_process(self):
        '''
        Stop the process (if running)
        '''
        return self._kill_all_processes()

    def _restart(self):
        '''
        restart the process
        '''
        self._stop_process()
        self._server_thread.join(1)
        self._start_server_thread()
