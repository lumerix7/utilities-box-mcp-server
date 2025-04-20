FROM python:3.13.3-slim

ENV LANG=en_US.utf8
ENV TZ=Asia/Shanghai

ARG EXTRA_INDEX_URL
ARG EXTRA_INDEX_HOST

RUN pip install utilities-box-mcp-server --no-cache-dir --extra-index-url $EXTRA_INDEX_URL --trusted-host=$EXTRA_INDEX_HOST

EXPOSE 41104

CMD ["utilities-box-mcp-server"]
