from src.container_funcs import (
    download_logs,
    create_and_run_container
)
from src.configs import log_info
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
from rich.console import Console
from rich.prompt import Prompt
import netifaces as ni
import argparse

console = Console()


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


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", dest="out_dir", default=".", help="Output pcaps and access log to this directory.")
    parser.add_argument("--capture-name", dest="cap_name", required=True, help="Naming scheme for captures.")

    args = parser.parse_args()
    console.log(f"{log_info} Starting capture server")
    create_and_run_container("https-logserver", "https-logserver.dockerfile", "", {})
    response = False
    while response != "Y":
        response = Prompt.ask("Done capturing? [Y/n]", default="Y")

    download_logs(args.cap_name, args.out_dir)

    calc_ja3_hashes("", args.out_dir)
    calc_ja4_hashes("", args.out_dir)

    all_ja3_files = get_log_paths(args.out_dir, "_ja3.json")
    all_ja4_files = get_log_paths(args.out_dir, "_ja4.json")
    get_unique_ja3(all_ja3_files)
    get_unique_ja4(all_ja4_files)


if __name__ == "__main__":
    main()
