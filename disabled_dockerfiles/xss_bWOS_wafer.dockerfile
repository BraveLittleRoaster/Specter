# Use an official Python runtime as a parent image
FROM ubuntu:latest
FROM python:3.8

# Version information
LABEL version="1.0.0"

# Set the working directory in the container
WORKDIR /usr/src/app

# Install dependencies for chromedriver and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    jq \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Download and install chromedriver
RUN LATEST_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json | jq -r '.milestones["125"].version'); wget -q "https://storage.googleapis.com/chrome-for-testing-public/$LATEST_VERSION/linux64/chromedriver-linux64.zip" -O chromedriver-linux64.zip; unzip -q chromedriver-linux64.zip -d /usr/local/bin/; rm chromedriver-linux64.zip

# Clone the wafer repository
RUN git clone https://github.com/sysdig/wafer

# Change the working directory to the wafer directory
WORKDIR /usr/src/app/wafer

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Create a non-root user and switch to it
RUN useradd -m chromeuser && chown -R chromeuser:chromeuser /usr/src/app
USER chromeuser

# Define environment variables
ENV APP_NAME "Wafer"
ENV CMDLINE_EXEC 'python3 wafer.py --url ${TARGET_URL} --param ${INJECTION_POINT} --headless'
ENV UPDATE_CMD "git pull origin main"

# Copy the start script to the container
COPY ./cmds/start.sh /usr/src/app/start.sh

# Use the start script in CMD
CMD ["/usr/src/app/start.sh"]
