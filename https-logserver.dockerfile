# Imports
FROM ubuntu:latest
FROM python:latest

USER root

# Install iproute2
RUN apt-get update && apt-get install -y iproute2

# Copy our scripts and binaries over
RUN mkdir /scripts
COPY ./src/jarm_randomizer.py /scripts/
COPY ./src/ecc_randomizer.py /scripts/
COPY ./src/capture_packets.py /scripts/
COPY ./src/honeypot.py /scripts/
COPY ./cmds/build.sh /scripts/
COPY ./cmds/entrypoint.sh /scripts/

# Install Dependencies
RUN apt-get update
# Make sure apt is in non-interactive mode or tzdata halts install
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y install nano cron python3-pip libpcap-dev libasan6 libpcre3-dev build-essential git mercurial libxml2 libxsltc-java libxslt1-dev
RUN pip3 install sanic scapy ujson
# Build NGINX
RUN /scripts/build.sh
COPY src/headers.js /etc/nginx/headers.js
RUN python3 /scripts/jarm_randomizer.py -c /etc/nginx/nginx.conf
# Build initial ECC certs
RUN python3 /scripts/ecc_randomizer.py

# Fire up the ghostpot server
EXPOSE 443/tcp

# Set the entrypoint to map local IPv4 to local.example.com for Nginx proxy_pass. This avoids IPs in request headers.
ENTRYPOINT ["/scripts/entrypoint.sh"]

CMD cron;/build/nginx/objs/nginx -c /etc/nginx/nginx.conf;python3 /scripts/honeypot.py & python3 /scripts/capture_packets.py
