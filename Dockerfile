FROM centos

MAINTAINER noone

RUN ["yum", "install", "-y", "python-virtualenv"]
WORKDIR /kluge_webapi/
RUN ["virtualenv", "env"]
ADD requirements.txt /kluge_webapi/
RUN ["/kluge_webapi/env/bin/pip", "install", "-r", "/kluge_webapi/requirements.txt"]
ADD  . /kluge_webapi/
RUN ["/kluge_webapi/env/bin/python", "setup.py", "install"]
CMD /kluge_webapi/env/bin/python /kluge_webapi/run_tornado.py