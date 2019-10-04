# -*- coding: utf-8 -*-
from __future__ import absolute_import
import mock
import unittest
import time

from click.testing import CliRunner

from shub import items, log, requests


class JobResourceTest(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def _test_prints_objects(self, cmd_mod, resource_name):
        objects = ['Object 1', 'Object 2']
        jobid = '1/2/3'
        with mock.patch.object(cmd_mod, 'get_job', autospec=True) as mock_gj:
            # Patch job.items.iter_json() to return our objects
            mock_gj.return_value._metadata_updated = time.time()
            mock_resource = getattr(mock_gj.return_value, resource_name)
            mock_resource.iter_json.return_value = objects
            result = self.runner.invoke(cmd_mod.cli, (jobid,))
            mock_gj.assert_called_once_with(jobid)
            self.assertIn("\n".join(objects), result.output)

    def _test_forwards_follow(self, cmd_mod):
        with mock.patch.object(cmd_mod, 'get_job'), \
             mock.patch.object(cmd_mod, 'job_resource_iter', autospec=True) \
             as mock_jri:
            self.runner.invoke(cmd_mod.cli, ('1/2/3',))
            self.assertFalse(mock_jri.call_args[1]['follow'])
            self.runner.invoke(cmd_mod.cli, ('1/2/3', '-f'))
            self.assertTrue(mock_jri.call_args[1]['follow'])

    def _test_resource_filter(self, cmd_mod):
        with mock.patch.object(cmd_mod, 'get_job'), \
             mock.patch.object(cmd_mod, 'job_resource_iter', autospec=True) \
             as mock_jri:
            self.runner.invoke(cmd_mod.cli, ('1/2/3',))
            self.assertFalse(mock_jri.call_args[1]['filter_'])
            self.runner.invoke(cmd_mod.cli, ('1/2/3', '--filter', '["foo"]'))
            self.assertEqual(mock_jri.call_args[1]['filter_'], '["foo"]')

    def test_items(self):
        self._test_prints_objects(items, 'items')
        self._test_forwards_follow(items)
        self._test_resource_filter(items)

    def test_requests(self):
        self._test_prints_objects(requests, 'requests')
        self._test_forwards_follow(requests)
        self._test_resource_filter(requests)

    def test_log(self):
        objects = [
            {'time': 0, 'level': 20, 'message': 'message 1'},
            {'time': 1450874471000, 'level': 50, 'message': 'message 2'},
        ]
        jobid = '1/2/3'
        with mock.patch.object(log, 'get_job', autospec=True) as mock_gj:
            mock_gj.return_value._metadata_updated = time.time()
            mock_gj.return_value.logs.iter_values.return_value = objects
            result = self.runner.invoke(log.cli, (jobid,))
            mock_gj.assert_called_once_with(jobid)
            self.assertIn('1970-01-01 00:00:00 INFO message 1', result.output)
            self.assertIn('2015-12-23 12:41:11 CRITICAL message 2', result.output)
        self._test_forwards_follow(log)
        self._test_resource_filter(log)

    def test_log_unicode(self):
        objects = [
            {'time': 0, 'level': 20, 'message': u'jarzębina'}
        ]
        jobid = '1/2/3'
        with mock.patch.object(log, 'get_job', autospec=True) as mock_gj:
            mock_gj.return_value._metadata_updated = time.time()
            mock_gj.return_value.logs.iter_values.return_value = objects
            result = self.runner.invoke(log.cli, (jobid,))
            mock_gj.assert_called_once_with(jobid)
            self.assertIn(u'1970-01-01 00:00:00 INFO jarzębina', result.output)


if __name__ == '__main__':
    unittest.main()
