import subprocess
import shutil
import socket
import logging
from datetime import datetime
import platform

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def run_command(cmd, description):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Running {description}...")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error: Failed to run {description}. Error message: {e.stderr}")
        return None

def command_exists(cmd):
    """Check if a command exists."""
    return shutil.which(cmd) is not None

def check_internet():
    """Check internet connectivity."""
    test_domains = ["google.com", "amazon.com", "cloudflare.com"]
    for domain in test_domains:
        try:
            socket.create_connection((domain, 80))
            logger.info(f"Internet connection is working (connected to {domain} successfully)")
            return True
        except OSError:
            pass
    logger.error("Error: No internet connection (failed to connect to test domains)")
    return False

def perform_ping(target):
    """Perform a ping test."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "5", target]
    output = run_command(command, f"ping to {target}")
    if output:
        lines = output.splitlines()
        for line in lines:
            if "avg" in line:
                avg_time = line.split('/')[-3]
                logger.info(f"Ping to {target} successful. Average round-trip time: {avg_time} ms")
                return
    logger.info(f"Ping to {target} failed or couldn't interpret results")

def perform_traceroute(target):
    """Perform a traceroute."""
    if command_exists("traceroute"):
        command = ["traceroute", target]
    elif command_exists("tracert"):
        command = ["tracert", target]
    else:
        logger.warning("Warning: traceroute/tracert command not found")
        return

    output = run_command(command, f"traceroute to {target}")
    if output:
        hop_count = len(output.splitlines()) - 1
        logger.info(f"Traceroute to {target} completed with {hop_count} hops")
    else:
        logger.info(f"Traceroute to {target} failed")

def check_dns(domain):
    """Check DNS resolution."""
    try:
        ip = socket.gethostbyname(domain)
        logger.info(f"DNS resolution for {domain} successful. IP: {ip}")
    except socket.gaierror:
        logger.info(f"DNS resolution for {domain} failed")

def check_open_ports():
    """Check open ports."""
    if command_exists("netstat"):
        command = ["netstat", "-tuln"]
        output = run_command(command, "netstat for open ports")
        if output:
            open_ports = [line.split()[3].split(':')[-1] for line in output.splitlines() if "LISTEN" in line]
            logger.info(f"Found {len(open_ports)} open ports: {', '.join(open_ports)}")
        else:
            logger.info("Failed to check open ports")
    else:
        logger.warning("Warning: netstat command not found")

def main():
    """Main function to run all diagnostics."""
    logger.info("Starting network diagnostics")

    if not check_internet():
        logger.info("Internet connectivity check failed. Proceeding with local diagnostics.")

    perform_ping("8.8.8.8")
    perform_traceroute("google.com")
    check_dns("example.com")
    check_open_ports()

    logger.info("Network diagnostics completed")

if __name__ == "__main__":
    main()
