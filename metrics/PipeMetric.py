#! /usr/bin/env python

import re
import os
import Metric
import select
import logging

logger = logging.getLogger('sauron')

class PipeMetric(Metric.Metric):
	def __init__(self, name, path, **kwargs):
		super(PipeMetric,self).__init__(name)
		self.patterns = dict([(k, re.compile(v)) for k,v in kwargs.items()])
		self.path = path
		try:
			os.mkfifo(self.path)
		except OSError:
			logger.warn('Path "%s" already exists. Treating like fifo...' % self.path)
		self.f    = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
		self.stat = os.fstat(self.f)
	
	def __del__(self):
		try:
			os.close(self.f)
		except ValueError:
			pass
	
	def values(self):
		# Alright, first get new stats on the file
		s = os.fstat(self.f)
		# The lines we've read
		lines = []
		# Now, see if the file was nuked
		# I'm not sure how this works. Checking inode might not really capture
		# what we're talking about. It certainly happens when the file is replaced,
		# but there /may/ be other times when it changes
		if s.st_ino != self.stat.st_ino:
			logger.warn('Inode for %s has changed' % self.path)
			os.close(self.f)
			self.f = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
		elif s.st_mtime > self.stat.st_mtime:
			# If it's been modified since we last checked...
			r, w, e = select.select([self.f], [], [], 0)
			# And it's not read-ready, then we have to actually re-open it
			if len(r) == 0:
				os.close(self.f)
				self.f = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
		
		# Now, remember the current stats
		self.stat = s		
		
		# Now, let's check to see if it's ready for some reading
		content = ''
		r, w, e = select.select([self.f], [], [], 0)
		while len(r):
			content += os.read(self.f, 1024)
			r, w, e = select.select([self.f], [], [], 0)
		
		# Now, split it into lines
		lines = content.strip().split('\n')
		
		# Now that we have all our lines, go ahead and try to match the regex to each line
		counts = dict([(k, 0) for k in self.patterns])
		for line in lines:
			for k, r in self.patterns.items():
				if r.search(line):
					counts[k] += 1
		return {
			'results' : dict([(k, (v, 'Count')) for k, v in counts.items()])
		}