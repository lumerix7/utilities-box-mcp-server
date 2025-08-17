#!/usr/bin/env bash
set -x

docker stop utilities-box-mcp-server
docker rm utilities-box-mcp-server

docker run -d \
  --name utilities-box-mcp-server \
  --restart unless-stopped \
  -e SIMP_LOGGER_LOG_LEVEL=DEBUG \
  -e UTILITIES_BOX_SSE_DEBUG_ENABLED=True \
  -e UTILITIES_BOX_TRANSPORT=sse \
  -p 41104:41104 \
  utilities-box-mcp-server:0.1.0
