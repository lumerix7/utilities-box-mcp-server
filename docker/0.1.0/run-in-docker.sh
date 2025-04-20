#!/usr/bin/env bash
set -x

docker stop utilities-box-mcp-server
docker rm utilities-box-mcp-server

docker run -d \
  --name utilities-box-mcp-server \
  --restart unless-stopped \
  -e UTILITIES_BOX_TRANSPORT=sse \
  -e UTILITIES_BOX_LOG_LEVEL=DEBUG \
  -p 41104:41104 \
  utilities-box-mcp-server:0.1.0
