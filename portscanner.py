#!/usr/bin/python3

# Import of required services
import socket
import concurrent.futures
import datetime
import subprocess
import sys

# Menu selection
print("=" * 50)
print("1. Simple port scanner")
print("2. Ping range to discover live hosts")
print("=" * 50)

choice = input("Choose an option (1 or 2): ")

if choice == '1':
    # Simple port scanner
    print("\nSimple Port Scanner")
    target = input("Enter IP or hostname, e.g., 127.0.0.1 or scanme.nmap.org): ")
    start_port = int(input("Start port (e.g., 1): "))
    end_port = int(input("End port (e.g., 1024): "))
    save_to_file = input("Save results to file? (y/n): ").lower() == 'y'

    # Convert hostname into an IP
    try:
        target_ip = socket.gethostbyname(target)
        print(f"\nHostname resolved to: {target_ip}")
    except:
        print("Cannot resolve hostname. Check input and try again.")
        exit()

    # Empty list to collect all open ports we find
    open_ports = []

    # Function to scan one port
    def scan_port(port):
        try:
            # Create a new TCP socket for this port check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 addresses, using TCP
            
            # Set a timeout so closed ports don't slow us down
            sock.settimeout(1)  # 1 second wait
            
            # Attempt to connect to the target IP and port
            connection_result = sock.connect_ex((target_ip, port))
            
            # Returns 0 if port is open
            if connection_result == 0:
                # Get the common service name
                try:
                    service_name = socket.getservbyport(port)
                except:
                    service_name = "unknown"
                
                # Try to get the banner
                try:
                    sock.send(b"\r\n")
                    banner_data = sock.recv(100)
                    banner = banner_data.decode('utf-8', errors='ignore')
                    if not banner:
                        banner = "(no banner found)"
                except:
                    banner = "(no banner found)"
                
                # Display result
                print(f"Port {port:5} | OPEN | {service_name:12} | {banner}")
                
                # Save to list
                open_ports.append((port, service_name, banner))
            
            sock.close()
        
        except:
            pass  # Ignore closed ports

    # Start scanning
    print(f"Scanning {target_ip} | Ports {start_port}-{end_port}\n")
    print(f"{'Port':<10} {'State':<10} {'Service':<15} {'Banner'}")
    print("=" * 60)
    
    # Mark time when scan starts
    start_time = datetime.datetime.now()
    
    # Use 100 threads to scan up to 100 ports at a time
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        ports_to_scan = range(start_port, end_port + 1)
        executor.map(scan_port, ports_to_scan)
    
    # Mark time scan ends, and calculate duration scan took
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    
    print("=" * 60 + "\n")
    print(f"Scan finished in {duration}")
    print(f"Found {len(open_ports)} open port(s)")
    
    # Save to file if requested
    if save_to_file and open_ports:
        filename = f"scan_results_{target_ip}_{start_port}-{end_port}.txt"
        with open(filename, "w") as f:
            f.write(f"Port Scanner Results\n")
            f.write(f"Target IP: {target_ip}\n")
            f.write(f"Scanned ports: {start_port}-{end_port}\n")
            f.write(f"Time taken: {duration}\n")
            f.write(f"Date of scan: {datetime.datetime.now()}\n")
            for port, service, banner in open_ports:
                f.write(f"Port {port} | OPEN | {service} | {banner}\n")
        
        print(f"Results saved to {filename}")

elif choice == '2':
    # Ping to discover live hosts
    print("\nPing - Discover Live Hosts")
    
    # Query for range of IP addresses
    base = input("Enter base network (e.g., 192.168.1.): ")
    if not base.endswith('.'):
        base += '.'  # Add dot if missing
    
    range_input = input("Enter range (e.g., 1-254): ")
    try:
        start, end = map(int, range_input.split('-'))
    except:
        print("Invalid range. Use format like 1-254")
        exit()
    
    print(f"\nPinging {base}{start} to {base}{end}...\n")
    
    # Empty list to store live IPs
    live_hosts = []
    
    # Function to ping IP address to check if it's live
    def ping_host(ip):
        param = '-n' if sys.platform.startswith('win') else '-c'
        result = subprocess.call(['ping', param, '1', '-w', '1', ip],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # If result == 0, ping was successful so host is live
        if result == 0:
            print(f"{ip} is LIVE")
            live_hosts.append(ip)
    
    # Create a list of all IP addresses to ping
    ips = [base + str(i) for i in range(start, end + 1)]
    
    # 50 threads to ping up to 50 IPs at a time
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(ping_host, ips)
    
    # Summary of ping result
    print(f"\nPing complete. Found {len(live_hosts)} live host(s).")

else:
	# Error message if user didn't input 1 or 2
    print("Invalid choice. Please enter 1 or 2.")
