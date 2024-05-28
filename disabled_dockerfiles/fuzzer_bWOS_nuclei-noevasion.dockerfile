# Use the latest Go image
FROM golang:latest

# Set the working directory
WORKDIR /app

# Install git and bash
RUN apt-get update && apt-get install -y git bash
COPY ./src/headers.txt ./app/headers.txt
# Install nuclei
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
RUN nuclei -update & nuclei -ut

# Define environment variables
ENV APP_NAME "nuclei-evasion"
# Note the --fuzzer option is looking for slip-ups in response encodings and tests 29 different cases.
# To generate a large amount of payloads run the command like below.
ENV CMDLINE_EXEC 'nuclei -duc -u ${TARGET_URL} -t ${TARGET_SCAN}'
ENV UPDATE_CMD "nuclei -update & nuclei -ut"

COPY ./cmds/start.sh /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Use the start script in CMD
CMD ["/usr/src/app/start.sh"]