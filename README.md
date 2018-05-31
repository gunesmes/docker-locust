# docker-locust
Run Locust in Dockers for performance testing.

Locust + Docker + Python + Master + Slave

## get the image
    docker pull gunesmes/docker-locust

## run the image with executing your tests
    docker run --rm --name locust -v $PWD:/locust gunesmes/docker-locust -f /locust locust-file.py

## write required python libraries inside the requirements.txt

In Dockerfile there is a step at the end of the process to install required libraries defined in the requirements.txt so you must add all your requirements inside this file as in following format:

  pyquery
  requests

## simpliest running the tags in run.sh

Ensure that you are in the project folder, and the path in run.py is correct

	~/d/simple_capybara (master ⚡) sh run.sh
	latest: Pulling from gunesmes/docker-capybara-chrome
	Digest: sha256:7a4e0051cd5483ced7f489f14dfc8dbcfc9b2957e4e77d5ee3c9aca077820b50
	Status: Image is up to date for gunesmes/docker-capybara-chrome:latest
	 - Running tests with tagged: search
	 - Running tests with tagged: navigate-video

	 - All processes done!
	 - 0 minutes and 27 seconds elapsed.


