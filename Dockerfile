FROM python:2.7.14
MAINTAINER ioriiod0@gmail.com

RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com numpy
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com scipy
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com pandas
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com gevent
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com flask
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com schema
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com flask_sockets

ADD . /marathon
RUN cd /marathon && python setup.py install
WORKDIR /marathon

CMD ["python","bin/run_server.py"]
