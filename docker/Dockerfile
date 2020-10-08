FROM tjhei/test-jenkins-slave

MAINTAINER timo.heister@gmail.com

USER root

RUN apt-get update && apt-get -qy install \
    python3 valgrind python3-dateutil python3-urllib3

USER dealii
WORKDIR $HOME

