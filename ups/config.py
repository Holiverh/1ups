
import logging
logger = logging.getLogger(__name__)

import os
import optparse

def _assert_exists(path, is_dir=False, default_content=""):
	"""
		Checks to make sure a file or directory exists. If it doesn't,
		will attempt to create it. If creation fails, will raise
		ImportError.
	
		If `is_dir` is True, `path` will be treated as a directory, else
		a file. Default is False.
		
		In the case of a file being created, `default_content` will
		attempt to be wrote to the file. If it fails, ImportError is
		raised.
	"""
	
	if is_dir:
		
		if not os.path.isdir(path):
			try:
				logger.debug("Creating '{0}'".format(path))
				os.makedirs(path)
			except OSError:
				logger.exception("Directory creation failed!")
				raise ImportError
	
	else:
		
		if not os.path.isfile(path):
			try:
				with open(path, "wb") as file_:
					file_.write(default_content)
			except IOError:
				logger.exception("File creation failed!")
				raise ImportError
				

base_directory = "/home/oliver/Projects/1ups/.ups"

archive_directory = os.path.join(base_directory, "archives")
repository_list = os.path.join(base_directory, "sources")
package_list_cache_directory = os.path.join(base_directory, "package_list_cache")

for path, is_dir, content in [
							(base_directory, True, ""),
							(archive_directory, True, ""),
							(repository_list, False, ""),
							(package_list_cache_directory, True, "")
							]:
				
	_assert_exists(path, is_dir, content)

repositories = []
with open(repository_list, "r") as repo_list_file:
	for line in repo_list_file:
		line = line.strip()
		
		if not line.startswith("#"):
			repositories.append(line)

option_parser = optparse.OptionParser()
options, args = option_parser.parse_args()

try:
	action = args[0].lower()
except IndexError:
	action = None

packages = args[1:] or []

del _assert_exists
del logger
del os
del optparse
del args
