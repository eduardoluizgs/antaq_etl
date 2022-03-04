FROM mcr.microsoft.com/mssql/server

USER root

RUN apt-get -y update  && \
        apt-get install -y curl && \
        curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
        apt-get install -y dos2unix

RUN mkdir -p /app
WORKDIR /app

COPY ./entrypoint.sh /app
COPY ./init-database.sh /app
COPY ./init-database.sql /app

RUN dos2unix *

RUN chmod +x /app/init-database.sh

EXPOSE 1433

USER mssql

ENTRYPOINT /bin/bash ./entrypoint.sh
