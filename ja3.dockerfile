# Use an official Python runtime as a parent image
FROM python:3.8

# Version information
LABEL version="1.0.0"

# Set the working directory in the container
WORKDIR /usr/src/app

# Clone the wafer repository
RUN git clone --depth 1 https://github.com/salesforce/ja3.git

# Change the working directory to the JA3 directory and install dependencies
WORKDIR /usr/src/app/ja3
RUN pip3 install --no-cache-dir -r python/requirements.txt

# Define environment variables
ENV APP_NAME "JA3"
ENV CMDLINE_EXEC 'python3 python/ja3.py -j /root/https_capture.pcap > /root/ja3_hashes.json'
ENV UPDATE_CMD "git pull origin master"

# Copy the start script to the container
COPY ./cmds/start.sh /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Use the start script in CMD
CMD ["/usr/src/app/start.sh"]