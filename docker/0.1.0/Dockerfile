#FROM python:3.13.3-slim
FROM ubuntu:24.04

ENV LANG=en_US.utf8
ENV TZ=Asia/Shanghai

RUN apt-get update --allow-insecure-repositories \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
        python3 \
        python-is-python3 \
        python3-pip \
        ca-certificates \
        iputils-ping \
        net-tools \
        curl \
    && apt clean

ARG EXTRA_INDEX_URL
ARG EXTRA_INDEX_HOST

RUN pip install utilities-box-mcp-server --no-cache-dir --extra-index-url $EXTRA_INDEX_URL --trusted-host=$EXTRA_INDEX_HOST --break-system-packages

EXPOSE 41104

CMD ["utilities-box-mcp-server"]
