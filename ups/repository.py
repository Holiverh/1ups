
import os
import urllib2
import urlparse
import json

import logging
logger = logging.getLogger(__name__)

import ups

class RepositoryError(Exception): pass

class Repository(object):
		
		def __init__(self, url):
			
			self.url = url
			if not self.url.endswith("/"):
				self.url += "/"
			
			self.packages_list_url = urlparse.urljoin(self.url, "list")
			self.packages_root_url = urlparse.urljoin(self.url, "packages/")
			
			# We should keep a local copy of the package list that the
			# server advertises to prevent having to redownload every
			# time.
			self._package_list_cache = os.path.join(
								ups.config.package_list_cache_directory,
								"{0}:{1}".format(
									urlparse.urlparse(self.url).netloc,
									urlparse.urlparse(self.url).path.replace("/", "-"))
								)
			
			self.load_package_list()
		
		def load_package_list(self):
			
			self.package_list = set({})
			
			if not os.path.isfile(self._package_list_cache):
				self.update_package_list_cache()
			else:
				with open(self._package_list_cache, "r") as file_:
					for package_name in file_:
						self.package_list.add(package_name.strip().lower())
		
		def update_package_list_cache(self):
			
			with open(self._package_list_cache, "w") as file_:
				logger.debug("Get: {0}".format(self.packages_list_url))
				file_.write(
					urllib2.urlopen(self.packages_list_url).read())
			
			self.load_package_list()
		
		def fetch_package(self, package_name):
			"""
				Builds a Package instance for `package_name` for this
				repository from the info file provided. If no info file
				is found or is invlaid will raises RepositoryError.  
			"""
			
			package_root_url = urlparse.urljoin(self.packages_root_url,
														package_name + "/")
			
			package_info_url = urlparse.urljoin(package_root_url, "info")
			package_archive_url = urlparse.urljoin(package_root_url, "archive")
			
			logger.debug("Get: {0}".format(package_info_url))
			try:
				info = json.loads(urllib2.urlopen(package_info_url).read())
				return ups.package.Package(self, package_root_url, info)
			except urllib2.HTTPError as e:
				raise RepositoryError(e)
			except ValueError as e:
				raise RepositoryError("Unable to parse info file: {0}".format(e))
