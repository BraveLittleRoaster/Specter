import subprocess
from subprocess import DEVNULL
import time
import json


def check_container(container_name):
    try:
        # Use subprocess to run the docker inspect command
        result = subprocess.run(
            ["docker", "inspect", "--format={{.State.Status}}", container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check the output
        status = result.stdout.strip()
        if status == "running":
            print(f"The container '{container_name}' is fully started and running.")
            return True
        else:
            print(f"The container '{container_name}' is not running. Current status: {status}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Failed to inspect the container '{container_name}': {e}")
        return False


def monitor_container(container_name, interval=.1):
    while True:
        if check_container(container_name):
            break
        time.sleep(interval)


def create_and_run_container(container_name, dockerfile_relative_path, server_ip, env_vars):
    if image_exists(container_name):
        if needs_update(dockerfile_relative_path, container_name):
            print(f"Updating Docker image '{container_name}'")
            build_docker_image(container_name, dockerfile_relative_path)
    else:
        print(f"Building Docker image '{container_name}'")
        build_docker_image(container_name, dockerfile_relative_path)

    if container_exists(container_name):
        print(f"Container '{container_name}' already exists. Removing it.")
        remove_cmd = ["docker", "rm", "-f", container_name]
        output, err = subprocess.Popen(remove_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        if err:
            print(f"Error removing existing container: {err}")
            print(f"Remove output: {output.decode()}")
            return

    print(f"Starting container '{container_name}'")
    if container_name == "https-logserver":
        start_capture_server()
    elif container_name == "ja3-analysis":
        run_ja3_analysis(ENV_VARS=env_vars)
    elif container_name == "ja4-analysis":
        run_ja4_analysis(ENV_VARS=env_vars)
    elif container_name == "nuclei-noevasion":
        run_nuclei_scan(ENV_VARS=env_vars)
    else:
        start_container(container_name, server_ip, env_vars)
        wait_for_container_to_run(container_name)


def container_exists(container_name):
    cmd = ["docker", "ps", "-a", "-q", "-f", f"name={container_name}"]
    output = subprocess.check_output(cmd)
    return output.strip() != b""


def start_capture_server(worker_num=None):
    if worker_num:
        run_args = ["docker", "run", "-dti", "--name", {worker_num}, "-p", "8443:443", "https-logserver"]
    else:
        run_args = ["docker", "run", "-dti", "--name", "https-logserver", "-p", "8443:443", "https-logserver"]
    try:
        subprocess.run(run_args)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Capture Server: {e.output.decode()}")


def download_logs(tool_name, directory="./captures"):
    down_https_args = ["docker", "cp", "https-logserver:/root/eth0_capture.pcap", f"{directory}/{tool_name}_https.pcap"]
    down_http_args = ["docker", "cp", "https-logserver:/root/lo_capture.pcap", f"{directory}/{tool_name}_http.pcap"]
    down_access_args = ["docker", "cp", "https-logserver:/var/log/nginx/access.log", f"{directory}/{tool_name}_access.log"]
    try:
        subprocess.run(down_https_args, check=True)
        subprocess.run(down_http_args, check=True)
        subprocess.run(down_access_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[{tool_name}] Error downloading logs: {e}")


def start_container(container_name, server_ip, env_vars):
    custom_hosts = ["testing.lab.local:127.0.0.1", f"www.example.com:{server_ip}"]
    run_args = ["docker", "run", "--name", container_name, "-d"]
    for key, value in env_vars.items():
        run_args += ["-e", f"{key}={value}"]
    for host_entry in custom_hosts:
        run_args += ["--add-host", host_entry]
    run_args.append(container_name)
    try:
        subprocess.check_output(run_args)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Docker container: {e.output.decode()}")


def wait_for_container_to_run(container_name):
    while True:
        if not is_container_running(container_name):
            print(f"Container '{container_name}' is has stopped running")
            break
        print(f"Waiting for container '{container_name}' to finish running...")
        time.sleep(1)


def image_exists(image_name):
    try:
        subprocess.check_call(["docker", "image", "inspect", image_name], stdout=DEVNULL, stderr=DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def is_container_running(container_name):
    cmd = ["docker", "container", "inspect", "-f", "{{.State.Running}}", container_name]
    try:
        output = subprocess.check_output(cmd)
        return output.strip().decode('utf-8') == "true"
    except subprocess.CalledProcessError:
        return False


def build_docker_image(container_name, dockerfile_relative_path):
    build_cmd = ["docker", "build", "-t", container_name, "-f", dockerfile_relative_path, "."]
    try:
        output = subprocess.check_output(build_cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image: {e.output.decode()}")


def needs_update(dockerfile_relative_path, container_name):
    try:
        dockerfile_version = extract_version_from_dockerfile(dockerfile_relative_path)
        current_version = get_current_image_version(container_name)
        return dockerfile_version != current_version
    except Exception as e:
        print(f"Error: {e}")
        return True  # Assume an update is needed if there's an error


def extract_version_from_dockerfile(dockerfile_path):
    try:
        with open(dockerfile_path, 'r') as file:
            for line in file:
                if "LABEL version=" in line:
                    return line.split('"')[1]
    except Exception as e:
        print(f"Error reading Dockerfile: {e}")
        raise
    return None  # Version not found


def get_current_image_version(image_name):
    print(f"Inspecting image {image_name}")
    try:
        output = subprocess.check_output(["docker", "inspect", image_name])
        inspect_data = json.loads(output)
        if inspect_data and 'Config' in inspect_data[0] and 'Labels' in inspect_data[0]['Config']:
            labels = inspect_data[0]['Config']['Labels']
            if 'version' in labels:
                return labels['version']
    except Exception as e:
        print(f"Error inspecting image: {e}")
        raise
    return None  # Version not found


def run_ja3_analysis(ENV_VARS):
    # docker run -v $(pwd)/captures/burpsuite-scan_https.pcap:/path/in/container/burpsuite-scan_https.pcap ja3-analysis
    capture_dir = ENV_VARS['capture_dir']
    run_args = ["docker", "run", "-dti", "--name", "ja3-analysis", "-v", f"{ENV_VARS['PCAP_FILE']}:/root/https_capture.pcap", "ja3-analysis"]
    download_file_args = ["docker", "cp", "ja3-analysis:/root/ja3_hashes.json", f"{capture_dir}/{ENV_VARS['tool_name']}_ja3.json"]
    try:
        subprocess.check_output(run_args)
        print(f"Downloading JA3 to {capture_dir}/{ENV_VARS['tool_name']}_ja3.json")
        wait_for_container_to_run('ja3-analysis')
        subprocess.check_output(download_file_args)
    except subprocess.CalledProcessError as e:
        print(f"[{ENV_VARS['PCAP_FILE']}] Error analyzing JA3 logs: {e.output.decode()}")


def run_ja4_analysis(ENV_VARS):
    # docker run -v $(pwd)/captures/burpsuite-scan_https.pcap:/path/in/container/burpsuite-scan_https.pcap ja3-analysis
    run_args = ["docker", "run", "-dti", "--name", "ja4-analysis", "-v",
                f"{ENV_VARS['PCAP_FILE']}:/root/capture.pcap", "ja4-analysis"]
    capture_dir = ENV_VARS['capture_dir']
    if "https" in ENV_VARS['PCAP_FILE']:
        download_file_args = ["docker", "cp", "ja4-analysis:/root/ja4_hashes.json", f"{capture_dir}/{ENV_VARS['tool_name']}_https_ja4.json"]
    else:
        download_file_args = ["docker", "cp", "ja4-analysis:/root/ja4_hashes.json", f"{capture_dir}/{ENV_VARS['tool_name']}_http_ja4.json"]
    try:
        subprocess.check_output(run_args)
        print(f"Downloading JA4 to for {ENV_VARS['tool_name']}")
        wait_for_container_to_run('ja4-analysis')
        subprocess.check_output(download_file_args)
    except subprocess.CalledProcessError as e:
        print(f"[{ENV_VARS['PCAP_FILE']}] Error analyzing JA4 logs: {e.output.decode()}")


def run_nuclei_scan(ENV_VARS):
    run_args = ["docker", "run", "-dti", "--name", "nuclei-noevasion",
                "-e", f"TARGET_SCAN={ENV_VARS['TARGET_SCAN']}",
                "-e", f"TARGET_URL={ENV_VARS['TARGET_URL']}",
                "nuclei-noevasion"]

    try:
        subprocess.check_output(run_args)
        wait_for_container_to_run("nuclei-evasion")
    except subprocess.CalledProcessError as e:
        print(f"Nuclei scan: {ENV_VARS['TARGET_SCAN']} failed with error: {e}")
