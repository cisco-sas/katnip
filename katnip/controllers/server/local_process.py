import os
from kitty.controllers.base import BaseController
from subprocess import Popen, PIPE
import time


class LocalProcessController(BaseController):
    '''
    LocalProcessController runs a server application using python's subprocess.Popen()
    It can restart the process upon exit, or at the beginning of each test

    :example:

        ::

            controller = LocalProcessController('PyHttpServer', '/usr/bin/python', ['-m', 'SimpleHttpServer', '1234'])
    '''

    def __init__(self, name, process_path, process_args, delay_after_start=None, start_each_test=False, logger=None):
        '''
        :param name: name of the object
        :param process_path: path to the target executable. note that it requires the actual path, not only executable name
        :param process_args: arguments to pass to the process
        :param delay_after_start: delay after opening a process, in seconds (default: None)
        :param start_each_test: should restart the process every test, or only upon failures (default: False)
        :param logger: logger for this object (default: None)
        '''
        super(LocalProcessController, self).__init__(name, logger)
        assert(process_path)
        assert(os.path.exists(process_path))
        self._process_path = process_path
        self._process_name = os.path.basename(process_path)
        self._process_args = process_args
        self._process = None
        self._delay_after_start = delay_after_start
        self._start_each_test = start_each_test

    def pre_test(self, test_number):
        '''start the victim'''
        super(LocalProcessController, self).pre_test(test_number)
        if self._start_each_test or not self._is_victim_alive():
            if self._process:
                self._stop_process()
            cmd = [self._process_path] + self._process_args
            self._process = Popen(cmd, stdout=PIPE, stderr=PIPE)
            if self._delay_after_start:
                time.sleep(self._delay_after_start)
        self.report.add('process_name', self._process_name)
        self.report.add('process_path', self._process_path)
        self.report.add('process_args', self._process_args)
        self.report.add('process_id', self._process.pid)

    def post_test(self):
        '''Called when test is done'''
        assert(self._process)
        if self._is_victim_alive():
            if self._start_each_test:
                self._stop_process()
            # if we should stop every test let us be over with it
        else:
            # if process is dead, than we should check the error code
            if self._process.returncode != 0:
                self.report.failed('return code is not zero: %s' % self._process.returncode)

        # if the process is dead, let's add all of its info to the report
        if not self._is_victim_alive():
            self.report.add('stdout', self._process.stdout.read())
            self.report.add('stderr', self._process.stderr.read())
            self.logger.debug('return code: %d', self._process.returncode)
            self.report.add('return_code', self._process.returncode)
            self._process = None
        super(LocalProcessController, self).post_test()

    def teardown(self):
        '''
        Called at the end of the fuzzing session, override with victim teardown
        '''
        self._stop_process()
        self._process = None
        super(LocalProcessController, self).teardown()

    def _stop_process(self):
        if self._is_victim_alive():
            self._process.terminate()
            time.sleep(0.5)
            if self._is_victim_alive():
                self._process.kill()
                time.sleep(0.5)
                if self._is_victim_alive():
                    raise Exception('Failed to kill client process')

    def _is_victim_alive(self):
        return self._process and (self._process.poll() is None)
