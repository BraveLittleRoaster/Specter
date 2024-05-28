import json
import re
import os
import base64
from json import JSONDecodeError
from rich.console import Console
import urllib.parse
from src.container_funcs import create_and_run_container
from src.configs import log_info

console = Console()


def get_log_paths(directory, endswith):
    matching_files = []

    # List all files in the given directory
    for file in os.listdir(directory):
        # Construct the full path to the file
        file_path = os.path.join(directory, file)

        # Check if it's a file and if it ends with the specified suffix
        if os.path.isfile(file_path) and file.endswith(endswith):
            matching_files.append(file_path)

    return matching_files


def parse_message(message):
    pattern = r'\[([^\]]+)\]'
    matches = re.findall(pattern, message)
    message_dict = {}
    for match in matches:
        key_value = match.split(' ', 1)
        if len(key_value) == 2:
            key, value = key_value
            message_dict[key] = value.strip('"')
    return message_dict


def parse_modsec_file(modsec_file):

    with open(modsec_file, 'r') as f:
        all_lines = f.readlines()
    f.close()
    audit_log = list()
    for _ in all_lines:
        audit_log.append(json.loads(_))

    for _ in audit_log:
        if "parsed_messages" not in _.keys():
            _['audit_data']['parsed_messages'] = list()
        try:
            audit_msg = _['audit_data']['messages']
        except KeyError as err:
            _['audit_data']['messages'] = list()
            audit_msg = _['audit_data']['messages']

        if audit_msg:
            for message in audit_msg:
                _['audit_data']['parsed_messages'].append(parse_message(message))

    with open(f"{modsec_file}-parsed.json", 'w') as wf:
        for _ in audit_log:
            wf.write(json.dumps(_) + "\n")


def clean_log_line(json_str):

    fixed_str = json_str.replace('\\":\\"', '":"').replace('\\",\\"', '","').replace('{\\"', '{"').replace('\\"},', '"},')
    return fixed_str


def parse_nginx_file(nginx_file):

    with open(nginx_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    access_log = list()
    for _ in lines:
        try:
            access_log.append(json.loads(clean_log_line(_)))
        except JSONDecodeError as err:
            print(f"Unable to decode JSON: {err}\t\tRaw log entry:")
            print(_)

    return access_log


def recursive_urldecode(encoded_str):
    # Function to decode %uXXXX Unicode sequences
    def decode_unicode_escapes(s):
        return re.sub(r'%u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)

    # Decode standard URL-encoded sequences
    decoded_str = urllib.parse.unquote(encoded_str)

    while '%' in decoded_str or '%u' in decoded_str:
        new_decoded_str = decode_unicode_escapes(decoded_str)
        new_decoded_str = urllib.parse.unquote(new_decoded_str)

        if new_decoded_str == decoded_str:
            break
        decoded_str = new_decoded_str

    return decoded_str


def get_unique_payloads(access_log):
    console.log(f"Extracting unique payloads from {access_log}")
    parsed_log = parse_nginx_file(access_log)
    unique_payloads = set()

    for _ in parsed_log:
        cleaned_payload = recursive_urldecode(_['request_uri'].replace("/?a=1", ""))
        cleaned_payload = cleaned_payload.replace("/?a=FUZZ", "")
        cleaned_payload = cleaned_payload.replace("/?a=", "")
        cleaned_payload = cleaned_payload.replace("/?echo=1", "")
        cleaned_payload = cleaned_payload.replace("?echo=", "")
        cleaned_payload = cleaned_payload.replace("/wp-admin/admin-ajax.php", "")
        cleaned_payload = cleaned_payload.replace("/wp-admin", "")
        cleaned_payload = cleaned_payload.replace("/robots.txt", "")
        if cleaned_payload != '':
            unique_payloads.add(recursive_urldecode(cleaned_payload))

    save_payloads = f"{access_log}.payloads"
    console.log(f"Saving payloads to {save_payloads}")
    with open(save_payloads, "w") as wf:
        for payload in unique_payloads:
            # Base64 encode the payload before writing
            encoded_payload = base64.b64encode(payload.encode()).decode()
            wf.write(encoded_payload + "\n")
    console.log(f"Found a total of {len(unique_payloads)} unique payloads within {access_log}")
    return unique_payloads


def calc_ja3_hashes(server_ip, crawl_dir):

    https_pcaps = get_log_paths(crawl_dir, endswith="_https.pcap")
    for pcap in https_pcaps:
        tool_name = os.path.basename(pcap).split('_')[0]
        console.log(f"{log_info} Extracting JA3 hashes from {pcap}...")
        ENV_VARS = {"PCAP_FILE": pcap, "tool_name": tool_name, "capture_dir": crawl_dir}
        create_and_run_container("ja3-analysis", "ja3.dockerfile", server_ip, ENV_VARS)


def calc_ja4_hashes(server_ip, crawl_dir):

    https_pcaps = get_log_paths(crawl_dir, endswith="_https.pcap")
    http_pcaps = get_log_paths(crawl_dir, endswith="_http.pcap")
    for pcap in https_pcaps:
        tool_name = os.path.basename(pcap).split('_')[0]
        console.log(f"{log_info} Extracting HTTPS JA4 hashes from {pcap}...")
        ENV_VARS = {"PCAP_FILE": pcap, "tool_name": tool_name, "capture_dir": crawl_dir}
        create_and_run_container("ja4-analysis", "ja4.dockerfile", server_ip, ENV_VARS)

    for pcap in http_pcaps:
        tool_name = os.path.basename(pcap).split('_')[0]
        console.log(f"{log_info} Extracting HTTP JA4 hashes from {pcap}...")
        ENV_VARS = {"PCAP_FILE": pcap, "tool_name": tool_name, "capture_dir": crawl_dir}
        create_and_run_container("ja4-analysis", "ja4.dockerfile", server_ip, ENV_VARS)
