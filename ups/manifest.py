
import json
import re
import getpass

vars_map = {
				# Should usally be an empty string, used for test-run
				# installations
				"ROOT": "/home/oliver/Projects/1ups/.ups/test-install",
				
				# System level directories. SHould only be used by
				# packages which are system-wide fundamental packages.
				"SYS_CONFIG": "%(ROOT)/etc",
				"SYS_LIB": "%(ROOT)/lib",
				"SYS_BIN": "%(ROOT)/sbin",
				
				# Application directories.
				"CONFIG": "%(ROOT)/home/%(USER)/.%(PACKAGE)",
				"BIN": "%(ROOT)/usr/bin",
				"INCLUDES": "%(ROOT)/usr/includes",
				"LIBS": "%(ROOT)/usr/libs",
				
				"USER": getpass.getuser(),
				}

class Manifest(dict):
	
	def __init__(self, path, **extra_vars):
		
		self.path = path
		with open(self.path) as f:
			self._raw = json.load(f)
		
		self.vars = dict(vars_map.items() + extra_vars.items())
		
		for dir_, paths in self._raw.iteritems():
			for path in paths:
				self[path] = self.expand_path(dir_)
		
	def expand_path(self, path):
		
		var_re = re.compile(r"%\(([A-Z_]+)\)")
		vars = var_re.findall(path)
		
		for var in vars:
			path = var_re.sub(self.expand_path(self.vars[var]), path, 1)
		
		return path
