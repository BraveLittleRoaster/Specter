import argparse
import os
import netifaces as ni
from src.container_funcs import (
    create_and_run_container,
    download_logs
)
from src.configs import (
    console,
    log_info,
    log_success
)
from src.parser_funcs import (
    get_log_paths,
    get_unique_payloads,
    calc_ja3_hashes,
    calc_ja4_hashes
)
from src.render_data_funcs import (
    get_unique_ja3,
    get_unique_ja4
)


def get_local_ip_address(iface):
    try:
        # Get the interface addresses
        addrs = ni.ifaddresses(iface)
        # Extract the IPv4 addresses
        ipv4_info = addrs[ni.AF_INET]
        # Return the first IPv4 address (assuming there is at least one)
        ipv4_address = ipv4_info[0]['addr']
        return ipv4_address
    except (ValueError, KeyError):
        # Handle cases where the interface does not exist or has no IPv4 address
        return "Interface not found or no IPv4 address assigned."


def process_single_dockerfile(dockerfile_fpath, server_ip, ENV_VARS):
    docker_filename = os.path.basename(dockerfile_fpath).replace(".dockerfile", "") # .rstrip(".dockerfile") was bugging out here. sqlmap_base would be `sqlmap_bas`
    print(f"DOCKER FILE NAME: {docker_filename} {dockerfile_fpath}")
    parts = docker_filename.split("_")
    tool_cat = parts[0]
    tool_meta = parts[1]
    tool_name = parts[2]

    config = {
        "tool_name": tool_name,
        "tool_cat": tool_cat,
        "tool_meta": tool_meta,
        "server_ip": server_ip,
        "dockerfile": dockerfile_fpath,
        "env_vars": ENV_VARS
    }
    console.log(f"{log_info} Starting capture server...")
    create_and_run_container("https-logserver",
                             "https-logserver.dockerfile", server_ip, {})
    console.log(f"{log_success} Capture server running on 0.0.0.0:8443")

    console.log(f"{log_info} Running {tool_name} against {ENV_VARS['TARGET_URL']}")
    create_and_run_container(tool_name, dockerfile_fpath, server_ip, env_vars=ENV_VARS)
    console.log(f"{log_success} Finished running {tool_name}. Downloading pcap files...")
    download_logs(tool_name)
    console.log(f"{log_info} {tool_name} done.")


def process_docker_files(server_ip, ENV_VARS):

    docker_files = list()

    console.log(f"{log_info} Searching for docker files to fuzz with...")
    for root, dirs, files in os.walk("./docker_files"):
        for file in files:
            if file.endswith(".dockerfile"):
                filepath = os.path.join(root, file)
                docker_files.append(filepath)

    if len(docker_files) > 0:
        console.log(f"{log_success} Found a total of {len(docker_files)}")

    for dockerfile in docker_files:
        process_single_dockerfile(dockerfile_fpath=dockerfile, server_ip=server_ip, ENV_VARS=ENV_VARS)

    access_logs = get_log_paths('./captures', "_access.log")

    for access_log in access_logs:
        console.log(f"{log_info} Saving all unique payloads in {access_log} to {access_log}.payloads")
        get_unique_payloads(access_log)


def main():

    parser = argparse.ArgumentParser(description='Tool for managing Docker containers to extract payloads and JA3, JA4+ hashes.')
    parser.add_argument('--listen-iface', dest="iface", default='eno2', help='Interface for packet capture')
    parser.add_argument('--dockerfile', help='Specific Dockerfile to process')
    parser.add_argument("--target-url", dest="targ_url", default="https://www.example.com:8443/?a=FUZZ", help="URL to send tools against.")
    parser.add_argument("--target-host", dest="targ_host", default="www.example.com", help="Hostname of the target to send tools against.")
    parser.add_argument("--target-port", dest="targ_port", default="8443", help="Port of the target to send tools against.")
    parser.add_argument("--target-path", dest="targ_path", default="/", help="Target URI path. Default: /")
    parser.add_argument("--injection-point", dest="inj_point", default="a", help="Parameter to inject to")
    parser.add_argument("--target-scan", dest="targ_scan", default="cves,misconfiguration", help="Nuclei -t scan configuration to run.")
    parser.add_argument("--data", dest="post_body", default="a=FUZZ", help="POST body to send with fuzzers against target.")
    parser.add_argument("--file-upload", dest="file_upload", default="", help="Used to point to a file for uploading webshells, etc.")
    parser.add_argument("--file-include", dest="file_include", default="", help="Used to point to a file for including in tools that can do LFI or RFI.")
    parser.add_argument("--remote-cmd", dest="remote_cmd", default="", help="Remote command to exec against target for PoCs that let you pass in something like --cmd 'ls -lah'")
    parser.add_argument("--capture-dir", dest="capture_dir", default="./captures", help="Directory to crawl for pcaps to render JA3/JA4+ hashes for")
    args = parser.parse_args()

    ENV_VARS = {
        "TARGET_URL": args.targ_url,
        "TARGET_HOST": args.targ_host,
        "TARGET_PORT": args.targ_port,
        "TARGET_PATH": args.targ_path,
        "INJECTION_POINT": args.inj_point,
        "POST_BODY": args.post_body,
        "TARGET_SCAN": args.targ_scan,
        "FILE_UPLOAD": args.file_upload,
        "FILE_INCLUDE": args.file_include,
        "REMOTE_CMD": args.remote_cmd,
    }
    # Set host ENV variables. This will change where the containers are pointed for fuzzing.
    for key, value in ENV_VARS.items():
        os.environ[key] = value
    server_ip = get_local_ip_address(args.iface)

    if args.dockerfile:
        process_single_dockerfile(args.dockerfile, server_ip, ENV_VARS)
    else:
        process_docker_files(server_ip, ENV_VARS)

    calc_ja3_hashes(server_ip, args.capture_dir)
    calc_ja4_hashes(server_ip, args.capture_dir)

    all_ja3_files = get_log_paths(args.capture_dir, "_ja3.json")
    all_ja4_files = get_log_paths(args.capture_dir, "_ja4.json")
    get_unique_ja3(all_ja3_files)
    get_unique_ja4(all_ja4_files)



if __name__ == "__main__":
    main()
