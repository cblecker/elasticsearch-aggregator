FROM registry.access.redhat.com/ubi8/ubi-minimal
LABEL maintainer "Chris Collins <chris.collins@redhat.com>"

RUN microdnf install -y python3 python3-pip
RUN pip3 install pylint

RUN mkdir /app
WORKDIR /app

COPY . ./

RUN pip3 install -r requirements.txt

# Ignore module name error
RUN pylint elasticsearch-aggregator.py -d C0103

ENTRYPOINT ["/app/elasticsearch-aggregator.py"]

