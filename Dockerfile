FROM centos

MAINTAINER noone

RUN ["yum", "install", "-y", "python-virtualenv"]
WORKDIR /kluge_webapi/
RUN ["virtualenv", "env"]
RUN ["source", "/kluge_webapi/env/bin/activate"]
ADD requirements.txt /kluge_webapi/
RUN ["pip", "install", "-r", "/kluge_webapi/requirements.txt"]
ADD  . /kluge_webapi/
RUN ["python", "setup.py", "install"]
CMD /bin/bash