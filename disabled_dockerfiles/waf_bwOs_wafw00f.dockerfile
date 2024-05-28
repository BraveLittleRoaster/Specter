# Use an official Python runtime as a parent image
FROM python:3.8

# Version information
LABEL version="1.0.0"

# Set the working directory in the container
WORKDIR /usr/src/app

# Clone the wafer repository
RUN git clone --depth 1 https://github.com/EnableSecurity/wafw00f.git

# Change dir and install requirements
WORKDIR /usr/src/app/wafw00f
RUN pip3 install setuptools
RUN python3 setup.py install

# Define environment variables
ENV APP_NAME "wafw00f"
# Note the --fuzzer option is looking for slip-ups in response encodings and tests 29 different cases.
# To generate a large amount of payloads run the command like below.
ENV CMDLINE_EXEC 'wafw00f -a -v -f json ${TARGET_URL}'
ENV UPDATE_CMD "git pull origin master"
# Copy the start script to the container
COPY ./cmds/start.sh /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Use the start script in CMD
CMD ["/usr/src/app/start.sh"]