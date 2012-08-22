
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
					format="%(asctime)s %(message)s",
					datefmt="%H:%M:%S")

import ups

if __name__ == "__main__":
	
	repos = []
	for repo_url in ups.config.repositories:
		repos.append(ups.repository.Repository(repo_url))
	
	if ups.config.action == "update-lists":
		
		for repo in repos:
			repo.update_package_list_cache()
	
	elif ups.config.action == "install":
		
		for package in ups.config.packages:
		
			repos = [repo for repo in repos if 
										package in repo.package_list]
			
			if not repos:
				logger.error("Package {0} not found".format(package))
				continue
			
			success = False
			for repo in repos:
				try:
					repo.fetch_package(package).install()
					success = True
					break
				except ups.repository.RepositoryError as e:
					logger.error(e)
				except ups.package.PackageError as e:
					logger.error(e)
				except:
					logger.exception("Was unable to install {0} from {1}".format(
																			package,
																			repo.url
																			))
			logger.info("{0} {1} installed".format(
													package,
													"not" if not success else ""
													))
