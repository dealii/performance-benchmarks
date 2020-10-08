FROM tjhei/test-jenkins-slave

MAINTAINER timo.heister@gmail.com

USER root

RUN apt-get update && apt-get -qy install \
    python3 valgrind python3-dateutil python3-urllib3 g++ cmake ninja-build

USER dealii
WORKDIR $HOME

