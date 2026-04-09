FROM python:3.8-alpine

COPY --from=tianon/gosu /gosu /usr/local/bin/
RUN \
  echo http://dl-2.alpinelinux.org/alpine/edge/community/ >> /etc/apk/repositories && \
  apk --no-cache add shadow

WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN adduser -D user

ENTRYPOINT [ "docker/entrypoint" ]