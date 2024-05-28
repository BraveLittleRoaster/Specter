#!/bin/bash
echo "[-] Creating directories..."
mkdir /etc/nginx
mkdir /etc/nginx/ssl
mkdir /etc/nginx/modules
mkdir /var/log/nginx
mkdir /usr/local/nginx
echo "[-] Building NGINX..."
mkdir /build
cd /build
hg clone http://hg.nginx.org/njs
git clone -b OpenSSL_1_1_1-stable --depth=1 https://github.com/openssl/openssl
git clone -b release-1.23.3 --depth=1 https://github.com/nginx/nginx
git clone https://github.com/phuslu/nginx-ssl-fingerprint
# Patch
patch -p1 -d openssl < nginx-ssl-fingerprint/patches/openssl.OpenSSL_1_1_1-stable.patch
patch -p1 -d nginx < nginx-ssl-fingerprint/patches/nginx-1.23.patch
# Configure & Build
cd nginx
ASAN_OPTIONS=symbolize=1 ./auto/configure --with-openssl=$(pwd)/../openssl --add-module=$(pwd)/../nginx-ssl-fingerprint --with-http_ssl_module --with-stream_ssl_module --with-http_v2_module --with-debug --with-stream --with-cc-opt="-fsanitize=address -O -fno-omit-frame-pointer" --with-ld-opt="-L/usr/local/lib -Wl,-E -lasan" --modules-path="/etc/nginx/modules" --error-log-path="/var/log/nginx/error.log" --add-module=$(pwd)/../njs/nginx
make
