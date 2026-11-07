#!/bin/bash
set -euo pipefail
cd /Users/ruisongde/Documents/deepseek-harness/default-workspace/inkwell

echo "Killing any old server on port 9030..."
lsof -ti:9030 | xargs kill -9 2>/dev/null || true
sleep 1

echo "Starting MCP server on port 9030..."
../.python3/bin/python3.14 mcp_server.py > /tmp/inkwell_mcp.log 2>&1 &
PID=$!
echo "Started PID $PID"

echo "Waiting for server to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:9030/health >/dev/null 2>&1; then
    echo "Server is HEALTHY on port 9030 (PID $PID)"
    exit 0
  fi
  sleep 1
done


echo "ERROR: Server did not start within 30 seconds."
echo "Last 10 log lines:"
tail -10 /tmp/inkwell_mcp.log
exit 1