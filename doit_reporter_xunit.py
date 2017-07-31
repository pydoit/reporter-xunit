import sys
from io import StringIO
import time
from xml.sax.saxutils import escape

from doit.reporter import TaskResult


class ReporterXunit(object):
    """Output in XML, xunit unit-test report
    """
    # short description, used by the help system
    desc = 'XML xunit output'

    def __init__(self, outstream, options=None): #pylint: disable=W0613
        # options parameter is not used
        # result is sent to stdout when doit finishes running

        # when using this reporter output can NOT contain any other
        # output than the XML data.
        # So anything that is sent to stdout/err needs to be captured.
        self._old_out = sys.stdout
        sys.stdout = StringIO() # TODO send to dev/null?
        self._old_err = sys.stderr
        sys.stderr = StringIO()
        self.outstream = outstream

        # runtime and cleanup errors
        self.t_results = {}

        self.errors = []
        self._start_time = None

    def initialize(self, tasks):
        """called just after tasks have been loaded before execution starts"""
        self._start_time = time.time()


    def get_status(self, task):
        """called when task is selected (check if up-to-date)"""
        self.t_results[task.name] = TaskResult(task)

    def execute_task(self, task):
        """called when execution starts"""
        self.t_results[task.name].start()

    def add_failure(self, task, exception):
        """called when execution finishes with a failure"""
        self.t_results[task.name].set_result('failure', exception.get_msg())

    def add_success(self, task):
        """called when execution finishes successfully"""
        self.t_results[task.name].set_result('success')

    def skip_uptodate(self, task):
        """skipped up-to-date task"""
        self.t_results[task.name].set_result('skipped', 'up-to-date')

    def skip_ignore(self, task):
        """skipped ignored task"""
        self.t_results[task.name].set_result('skipped', 'ignored')

    def cleanup_error(self, exception):
        """error during cleanup"""
        self.errors.append(exception.get_msg())

    def runtime_error(self, msg):
        """error from doit (not from a task execution)"""
        self.errors.append(msg)

    def teardown_task(self, task):
        """called when starts the execution of teardown action"""
        pass

    def complete_run(self):
        """called when finished running all tasks"""
        # restore stdout
        sys.stdout = self._old_out
        sys.stderr = self._old_err

        print('''<?xml version="1.0" encoding="utf-8"?>''')
        summary = {
            'errors': len(self.errors),
            'failures': len([x for x in self.t_results.values() if x.result=='failure']),
            'skips': len([x for x in self.t_results.values() if x.result=='skipped']),
            'name': 'doit',
            'num_tasks': len(self.t_results),
            'time': time.time() - self._start_time,
        }
        print('''<testsuite errors="{errors}" failures="{failures}" name="{name}" skips="{skips}" tests="{num_tasks}" time="{time}">'''.format(**summary))
        for result in self.t_results.values():
            if result.elapsed is None:
                if result._started_on:
                    result.elapsed = result._finished_on - result._started_on
                else:
                    result.elapsed = 0.0

            tsum = {
                'name': result.task.name,
                'time': result.elapsed,
            }
            # TODO file, line, classname
            print('''\n<testcase name="{name}" time="{time:0.3f}">'''.format(**tsum))
            if result.error:
                print('''<{tag} message="">{content}</{tag}'''.format(tag=result.result, content=escape(result.error)))
            if result.out:
                print('''<system-out>{}</system-out>'''.format(escape(result.out)))
            if result.err:
                print('''<system-err>{}</system-err>'''.format(escape(result.err)))
            print('''</testcase>''')

            # this is not part of xunit, but need a way to reporter
            # errors out of tests.
            if self.errors:
                print('''<errors>{}</errors>'''.format(escape("\n".join(self.errors))))
        print('''</testsuite>''')
