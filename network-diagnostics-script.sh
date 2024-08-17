#!/bin/bash

# Network Diagnostics Script

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run a command with error handling
run_command() {
    local cmd="$1"
    local description="$2"
    
    log "Running $description..."
    if ! output=$(eval "$cmd" 2>&1); then
        log "Error: Failed to run $description. Error message: $output"
        return 1
    fi
    echo "$output"
    return 0
}

# Function to check internet connectivity
check_internet() {
    local test_domains=("google.com" "amazon.com" "cloudflare.com")
    for domain in "${test_domains[@]}"; do
        if ping -c 3 "$domain" >/dev/null 2>&1; then
            log "Internet connection is working (pinged $domain successfully)"
            return 0
        fi
    done
    log "Error: No internet connection (failed to ping test domains)"
    return 1
}

# Function to perform ping test
perform_ping() {
    local target="$1"
    local output
    
    output=$(run_command "ping -c 5 $target" "ping to $target")
    if [ $? -eq 0 ]; then
        local avg_time=$(echo "$output" | tail -1 | awk -F '/' '{print $5}')
        log "Ping to $target successful. Average round-trip time: $avg_time ms"
    else
        log "Ping to $target failed"
    fi
}

# Function to perform traceroute
perform_traceroute() {
    local target="$1"
    local output
    
    if command_exists traceroute; then
        output=$(run_command "traceroute $target" "traceroute to $target")
        if [ $? -eq 0 ]; then
            local hop_count=$(echo "$output" | wc -l)
            log "Traceroute to $target completed with $hop_count hops"
        else
            log "Traceroute to $target failed"
        fi
    else
        log "Warning: traceroute command not found"
    fi
}

# Function to check DNS resolution
check_dns() {
    local domain="$1"
    local output
    
    output=$(run_command "nslookup $domain" "DNS lookup for $domain")
    if [ $? -eq 0 ]; then
        local ip=$(echo "$output" | awk '/^Address: / { print $2 }')
        log "DNS resolution for $domain successful. IP: $ip"
    else
        log "DNS resolution for $domain failed"
    fi
}

# Function to check open ports
check_open_ports() {
    local output
    
    if command_exists netstat; then
        output=$(run_command "netstat -tuln" "netstat for open ports")
        if [ $? -eq 0 ]; then
            local port_count=$(echo "$output" | grep LISTEN | wc -l)
            log "Found $port_count open ports"
        else
            log "Failed to check open ports"
        fi
    else
        log "Warning: netstat command not found"
    fi
}

# Main function
main() {
    log "Starting network diagnostics"
    
    if ! check_internet; then
        log "Internet connectivity check failed. Proceeding with local diagnostics."
    fi
    
    perform_ping "8.8.8.8"
    perform_traceroute "google.com"
    check_dns "example.com"
    check_open_ports
    
    log "Network diagnostics completed"
}

# Run the main function
main
