
import logging
logger = logging.getLogger(__name__)

import os
import tarfile
import urllib2
import urlparse

import ups

class PackageError(Exception): pass

class Package(object):
	
	def __init__(self, repo, url, info):
		
		self.repository = repo
		self.url = url
		self.info_url = urlparse.urljoin(self.url, "info")
		
		
		self.name = info["name"]
		self.description = info.get("description", "")
		
		self.dependencies = [repo.fetch_package(pkg_name) for pkg_name 
										in info.get("dependencies", [])]
		
		archive_name = info.get("archive", "archive.tar")
		archive_extension = ".".join(archive_name.split(".")[1:])
		
		self.archive_url = urlparse.urljoin(self.url, archive_name)
		self.archive_path = os.path.join(ups.config.archive_directory,
											self.name + "." + archive_extension)
		
		self.manifest_url = urlparse.urljoin(self.url, "manifest")
		self.manifest_path = os.path.join(ups.config.archive_directory, self.name + ".manifest")
		
	def download(self):
		
		for url, path in [(self.archive_url, self.archive_path),
							(self.manifest_url, self.manifest_path)]:
			
			logger.debug("Get: {0}".format(url))
			
			with open(path, "wb") as file_:
				file_.write(urllib2.urlopen(url).read())
		
	def install(self, skip_deps=False):
		
		if not skip_deps:
			for dep in self.dependencies:
				try:
					dep.install()
				except PackageError as e:
					raise PackageError("Dependancy ({0}) error: {1}".format(
																			dep.name,
																			e))
				
		if (not os.path.isfile(self.archive_path) or 
					not tarfile.is_tarfile(self.archive_path)):
			self.download()
		
		logger.info("Installing {0}".format(self.name))
		
		try:
			archive = tarfile.open(self.archive_path)
			manifest = ups.manifest.Manifest(self.manifest_path, PACKAGE=self.name)
			
			# Check to make sure the manifest is complete
			for member in archive.getmembers():
				
				try:
					dest = manifest[member.name]
				except KeyError:
					raise PackageError("Broken manifest; no map for {0}".format(
																		member.name))
				
				if member.name.find("..") != -1 or member.name.startswith("/"):
					raise PackageError("Archive member {0} is absolute or uses '..'".format(
																				member.name))
																				
				logger.debug("Extract: {0} to {1}".format(member.name, dest))
				archive.extract(member, dest)
			
		finally:
			archive.close()
