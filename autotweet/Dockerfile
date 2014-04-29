FROM ubuntu:precise
MAINTAINER Kevin Manley <kevin.manley@gmail.com> 

# Tell debconf to run in non-interactive mode
ENV DEBIAN_FRONTEND noninteractive

# Check we've got the lastest distr
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
# update the box
RUN apt-get update

RUN apt-get install -y python2.7 python-setuptools

RUN pip install requests
RUN pip install python-twitter 

ADD autotweet.py

CMD python autotweet.py

