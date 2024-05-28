# Use an official Python runtime as a parent image
FROM python:3.8

# Version information
LABEL version="1.0.0"

# Set the working directory in the container
WORKDIR /usr/src/app

# Clone the wafer repository
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev

# Change the working directory to the wafer directory
WORKDIR /usr/src/app/sqlmap-dev

# Define environment variables
ENV APP_NAME "SQLmap"
ENV CMDLINE_EXEC 'python3 sqlmap.py -p a --tmp-dir=/tmp --no-logging --flush-session --batch --random-agent --url ${TARGET_URL} -p ${INJECTION_POINT} --level 5 --risk 3 --all --tamper=bluecoat,charunicodeencode,luanginx,modsecurityversioned,modsecurityzeroversioned,randomcase,randomcomments,space2comment,space2hash,space2plus,varnish,xforwardedfor'
ENV UPDATE_CMD "git pull origin master"
# Copy the start script to the container
COPY ./cmds/start.sh /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Use the start script in CMD
CMD ["/usr/src/app/start.sh"]