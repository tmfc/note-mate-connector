#!/bin/bash
echo "构建镜像"
docker build -t tmfc/note-mate-wx-connector .

docker tag tmfc/note-mate-wx-connector docker.willking.tech/tmfc/note-mate-wx-connector:latest
echo "推送镜像"
docker push docker.willking.tech/tmfc/note-mate-wx-connector:latest



