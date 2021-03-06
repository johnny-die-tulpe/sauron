#! /usr/bin/env python
#
# Copyright (c) 2011 SEOmoz
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import datetime
from sauron import logger
from sauron.metrics import Metric, MetricException

class DiskMetric(Metric):
    def __init__(self, name, serializer, path, **kwargs):
        Metric.__init__(self, name, serializer, **kwargs)
        self.reconfig(name, serializer,  path, **kwargs)

    def reconfig(self, name, serializer, path, **kwargs):
        Metric.reconfig(self, name, serializer, **kwargs)
        self.path = path

    def values(self):
        # Reference:
        # http://stackoverflow.com/questions/787776/find-free-disk-space-in-python-on-os-x
        try:
            st = os.statvfs(self.path)
            divisor = 1024.0 ** 3
            free  = (st.f_bavail * st.f_frsize) / divisor
            total = (st.f_blocks * st.f_frsize) / divisor
            used  = (st.f_blocks - st.f_bavail) * st.f_frsize / divisor
            results = {
                    'free'       : (round(free , 3), 'Gigabytes'),
                    'total'      : (round(total, 3), 'Gigabytes'),
                    'used'       : (round(used , 3), 'Gigabytes'),
                    'percent'    : (round(float(used) / float(total), 3) * 100, 'Percent'),
                    'inodes'     : (st.f_files, 'Count'),
                    'ifree'      : (st.f_ffree, 'Count'),
                    'iused_perc' : (round(float(st.f_files - st.f_ffree) / float(st.f_files), 3) * 100, 'Percent'),
            }
            return {'results': results}
        except Exception as e:
            raise MetricException(e)
