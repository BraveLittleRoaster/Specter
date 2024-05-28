import time
import subprocess
import argparse
import os.path
from rich.console import Console
from src.parser_funcs import get_log_paths
from src.container_funcs import create_and_run_container, download_logs, monitor_container
from src.configs import log_info, log_success, log_error
from specter import get_local_ip_address
from multiprocessing.dummy import Pool

console = Console()
target_url = ""
server_ip = ""


def capture_nuclei_cves(target_url, use_evasion):

    all_nuclei_templates = get_log_paths(f"{os.path.expanduser('~')}/nuclei-templates/http/cves", ".yaml")

    for nuclei_template in all_nuclei_templates:
        cve = os.path.basename(nuclei_template).replace(".yaml", "")
        if "example.com" in target_url:
            console.log(f"{log_info} {nuclei_template} Starting capture server...")
            create_and_run_container("https-logserver","https-logserver.dockerfile",
                                     "", {})
            time.sleep(.3)  # Make sure container is fully started

        if use_evasion:
            nuclei_args = ["nuclei", "-duc", "-u", target_url, "-t", nuclei_template, "-H", "src/headers.txt", "-tlsi"]
        else:
            nuclei_args = ["nuclei", "-duc", "-u", target_url, "-t", nuclei_template]
        try:
            subprocess.run(nuclei_args)
        except subprocess.CalledProcessError as e:
            console.log(f"{log_error} Nuclei scan failed for {cve}: {e}")
        console.log(f"{log_success} Done scanning {cve} against {target_url}... Downloading pcaps")
        download_logs(cve, directory="./captures/nuclei-cves")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default="https://www.example.com:8443/", help="URL to target nuclei scans against.")
    parser.add_argument("--use-evasion", dest="evasion", action="store_true", help="Use -tlsi and Header Order spoofing for JA3/JA4+ evasion.")
    args = parser.parse_args()

    global target_url
    target_url = args.url
    global server_ip
    server_ip = get_local_ip_address(args.iface)
    capture_nuclei_cves(args.url, args.evasion)


if __name__ == "__main__":
    main()
