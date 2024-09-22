#!/bin/bash
echo "build..."
docker build -t wanted-jjh .

echo "cleanup container..."
docker rm -f wanted-jjh

echo "run container..."
docker run -itd -p 8000:8000 --name=wanted-jjh wanted-jjh /bin/bash

echo "sleep 1"
sleep 1

echo "docker logs:"
docker logs wanted-jjh

echo "deploy done."