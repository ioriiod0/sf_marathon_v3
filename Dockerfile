FROM python:3.7
MAINTAINER ioriiod0@gmail.com

RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com numpy
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com aiohttp
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com sanic
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com schema

ADD . /marathon
RUN cd /marathon && python setup.py install
WORKDIR /marathon

CMD ["python","bin/run_server.py"]
