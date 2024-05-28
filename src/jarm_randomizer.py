import random
import argparse


def randomize_chipers():

    ciphers = [
        "EECDH+ECDSA+AESGCM",
        "EECDH+aRSA+AESGCM",
        "EECDH+ECDSA+SHA384",
        "EECDH+ECDSA+SHA256",
        "EECDH+aRSA+SHA384",
        "EECDH+aRSA+SHA256",
        "EECDH+aRSA+RC4",
        "EECDH",
        "EDH+aRSA",
        "RC4",
        "!aNULL",
        "!eNULL",
        "!LOW",
        "!3DES",
        "!MD5",
        "!EXP",
        "!PSK",
        "!SRP",
        "!DSS",
        "ECDHE-ECDSA-CHACHA20-POLY1305",
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "DHE-RSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-RSA-CHACHA20-POLY1305"
    ]

    random.shuffle(ciphers)
    return ":".join(ciphers)


def randomize_curve():

    curves = [
        "secp521r1",
        "secp384r1",
        "prime256v1"
    ]

    return curves[random.randint(0, 2)]

def randomize_tls_version():

    tls_versions = [
        "TLSv1",
        "TLSv1.1",
        "TLSv1.2",
        "TLSv1.3"
    ]

    random.shuffle(tls_versions)
    return " ".join(tls_versions[:-1])


def main():

    parser = argparse.ArgumentParser("nginx config JARM randomizer")
    parser.add_argument("-c", "--config", dest="config", required=True, help="Path to the config file.")

    args = parser.parse_args()

    nginx_config = f"""
worker_processes auto;
daemon on;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;
error_log /var/log/nginx/error.log;
events {{
    worker_connections  1024;
}}

http {{
    js_import /etc/nginx/headers.js;
    js_set $headers_json headers.headers_json;
    log_format custom escape=json '{{"remote_addr": "$remote_addr",'
                                    '"time_local": "$time_local",'
                                    '"request": "$request", "request_method": "$request_method", "request_uri": "$request_uri",'
                                    '"status": $status,'
                                    '"user_agent": "$http_user_agent",'
                                    '"headers": $headers_json,'
                                    '"http_ssl_ja3": "$http_ssl_ja3", "http_ssl_ja3_hash": "$http_ssl_ja3_hash",'
                                    '"request_body": "$request_body"}}';
    server {{
        access_log /var/log/nginx/access.log custom;
        proxy_busy_buffers_size 512k;
        proxy_buffers 4 512k;
        proxy_buffer_size 256k;
        proxy_pass_header Server;
        listen                 0.0.0.0:443 ssl;
        ssl_protocols          {randomize_tls_version()};
        ssl_dhparam            /etc/nginx/ssl/dhparam.pem;
        ssl_prefer_server_ciphers   on;
        ssl_ciphers            "{randomize_chipers()}";
        ssl_ecdh_curve         "{randomize_curve()}";
        ssl_certificate_key    /etc/nginx/ssl/server.key;
        ssl_certificate        /etc/nginx/ssl/server.crt;
        location ^~ / {{
            proxy_pass             http://local.example.com:8000;
        }}
    }}
}}
    """

    try:
        with open(args.config, 'w') as wf:
            wf.write(nginx_config)
        wf.close()
    except Exception as e:
        print(f"Please enter a valid filepath for --config. Ex: --config /etc/nginx/nginx.conf. Error: {e}")


if __name__ == "__main__":
    main()
