import urllib3
import ssl
from collections import OrderedDict
import random

class RandomizedCiphersHTTPSConnection(urllib3.connection.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        self.ciphers = kwargs.pop('ciphers', None)
        super().__init__(*args, **kwargs)

    def connect(self):
        self.ssl_context = ssl.create_default_context()
        if self.ciphers:
            self.ssl_context.set_ciphers(self.ciphers)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.sock = self._new_conn()
        self.sock.settimeout(self.timeout)
        self.sock = self.ssl_wrap_socket(self.sock, server_hostname=self.host)

def get_randomized_ciphers():
    ciphers = [
        "ECDH+AESGCM",
        "DH+AESGCM",
        "ECDH+AES256",
        "DH+AES256",
        "ECDH+AES128",
        "DH+AES",
        "ECDH+HIGH",
        "DH+HIGH",
        "ECDH+3DES",
        "DH+3DES",
        "RSA+AESGCM",
        "RSA+AES",
        "RSA+HIGH",
        "RSA+3DES",
        "!aNULL",
        "!eNULL",
        "!MD5"
    ]
    random.shuffle(ciphers)
    ciphers = ciphers[:-1]
    ciphers = ':'.join(ciphers)
    print(f"[-] Using CIPHERS: {ciphers}")
    return ciphers

def main():
    headers = OrderedDict([
        ('sec-ch-ua', '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"'),
        ('sec-ch-ua-mobile', '?0'),
        ('sec-ch-ua-platform', '"Linux"'),
        ('Upgrade-Insecure-Requests', '1'),
        ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'),
        ('Sec-Fetch-Site', 'none'),
        ('Sec-Fetch-Mode', 'navigate'),
        ('Sec-Fetch-User', '?1'),
        ('Sec-Fetch-Dest', 'document'),
        ('Accept-Encoding', 'gzip, deflate, br, zstd'),
        ('Accept-Language', 'en-US,en;q=0.9')
    ])

    ciphers = get_randomized_ciphers()
    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers(ciphers)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Suppress only the single InsecureRequestWarning from urllib3 needed.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    http = urllib3.PoolManager(
        num_pools=1,
        headers=headers,
        ssl_context=ssl_context
    )

    url = "https://www.example.com:8443/"
    response = http.request('GET', url, headers=headers, retries=False, timeout=10.0)

    print(response.data)

if __name__ == "__main__":
    main()
