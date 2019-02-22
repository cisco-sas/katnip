from time import sleep
import json
import signal
from pygdbmi.gdbcontroller import GdbController
from kitty.monitors.base import BaseMonitor


class GdbMiReport():
    def __init__(self, response):
        # Filter spam console messages
        self.console = list(filter(lambda x: x['type'] == 'console', response))
        self.notify = list(filter(lambda x: x['type'] == 'notify', response))
        self.result = list(filter(lambda x: x['type'] == 'result', response))
        self.log = list(filter(lambda x: x['type'] == 'log', response))
        self.stopped_payload = {}

    def is_stopped(self):
        for item in self.notify:
            if item['message'] == 'stopped':
                self.stopped_payload = item['payload']
                return True
        return False

    def get_result(self):
        for item in self.result:
            return item['message']
        return None

    def get_error(self):
        for item in self.result:
            if item['message'] == 'error':
                return item['payload']['msg']
        return None

    def get_console_log(self):
        result = ''
        for item in self.console:
            if item['message'] is None:
                result += item['payload'].replace('\\n', '\n')
        return result


class GdbServerMonitor(BaseMonitor):
    '''
    GdbServerMonitor monitors gdbserver
    :examples:

        Run gdbserver :port --attach <pid>
        ::
            import signal
            watch_signals = [signal.SIGSEGV, signal.SIGTERM]
            monitor = GdbServerMonitor('Gdb Monitor', '/usr/bin/gdb', '192.168.0.1', 2222, watch_signals)
    '''

    def __init__(self, name, gdb_path, host, port, signals=[signal.SIGSEGV], response_timeout=0.1, logger=None):
        '''
        :param name: name of the monitor object
        :param gdb_path: path to gdb binary
        :param host: target host
        :param port: target port
        :param signals: watch signal list
        :param logger: logger for the monitor object
        '''
        super(GdbServerMonitor, self).__init__(name, logger)
        self.gdbmi = GdbController(gdb_path=gdb_path, time_to_check_for_additional_output_sec=30)
        self.target_host = host
        self.target_port = port
        self.is_attached = False
        self.response_timeout = response_timeout
        self.watch_signals = list(map(lambda x: x.name, signals))

    def setup(self):
        response = self.gdbmi.write(
            'target remote %s:%d' % (self.target_host, self.target_port),
            timeout_sec=1,
            raise_error_on_timeout=True
        )
        self.logger.debug('[GDB] Command(target.remote) %s' % json.dumps(response))
        report = GdbMiReport(response)
        if report.get_result() == 'done':
            response = self.gdbmi.write('-exec-continue', raise_error_on_timeout=False)
            self.logger.debug('[GDB] Command(-exec-continue) %s' % json.dumps(response))
            self.is_attached = True
        else:
            self.logger.error(report.get_error())
        super(GdbServerMonitor, self).setup()

    def teardown(self):
        self.gdbmi.write('detach', raise_error_on_timeout=False)
        response = self.gdbmi.write('quit', raise_error_on_timeout=False)
        self.logger.debug('[GDB] Command(quit) %s' % json.dumps(response))
        super(GdbServerMonitor, self).teardown()

    def pre_test(self, test_number):
        if not self.is_attached:
            self.setup()
        super(GdbServerMonitor, self).pre_test(test_number)

    def post_test(self):
        response = self.gdbmi.get_gdb_response(timeout_sec=self.response_timeout, raise_error_on_timeout=False)
        self.logger.debug('[GDB] Command(alive) %s' % json.dumps(response))
        gdb_report = GdbMiReport(response)
        if gdb_report.is_stopped():
            self.report.failed('The program has stopped: %s' % gdb_report.stopped_payload)
            if gdb_report.stopped_payload.get('signal-name') in self.watch_signals:
                sig_name = gdb_report.stopped_payload.get('signal-name')
                addr = gdb_report.stopped_payload['frame'].get('addr')
                func = gdb_report.stopped_payload['frame'].get('func')
                from_target = gdb_report.stopped_payload['frame'].get('from')
                thread_id = gdb_report.stopped_payload.get('thread-id')
                # Write report
                self.logger.warning('Has signal: %s' % sig_name)
                self.report.failed('Thread: %s Signal: %s Func: %s ( %s ) %s' % (
                    thread_id, sig_name, func, addr, from_target
                ))
                # Write backtrace
                response = self.gdbmi.write('bt', raise_error_on_timeout=False)
                self.report.failed('Backtrace: %s' % GdbMiReport(response).get_console_log())
                input('Check if need restart')
                self.is_attached = False
            else:
                response = self.gdbmi.write('-exec-continue')  # continue if not interesting
                self.logger.debug('[GDB] Command(-exec-continue) %s' % json.dumps(response))
        super(GdbServerMonitor, self).post_test()

    def _monitor_func(self):
        sleep(0.1)
