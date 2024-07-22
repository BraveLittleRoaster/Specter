# Use an official Python runtime as a parent image
FROM python:latest

# Version information
LABEL version="1.0.0"

# Set the working directory in the container
WORKDIR /usr/src/app

# Clone the wafer repository
RUN git clone --depth 1 https://github.com/FoxIO-LLC/ja4.git

# Change the working directory to JA4 and install dependencies
WORKDIR /usr/src/app/ja4
RUN apt-get update && apt-get -y install tshark && apt-get clean

# Define environment variables
ENV APP_NAME="JA4"
ENV CMDLINE_EXEC='python3 python/ja4.py --json /root/capture.pcap -f /root/ja4_hashes.json'
ENV UPDATE_CMD="git pull origin master"

# Copy the start script to the container
COPY ./cmds/start.sh /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Use the start script in CMD
CMD ["/usr/src/app/start.sh"]
