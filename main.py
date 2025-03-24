## TO-DO: ABUSEIPDB Report

import json, time, os, logging, traceback, sys, requests, signal
from datetime import datetime

# Initialize
cowrie_log_path = ''
output_log_path = 'output'
tokens = {}

# IP Log & Error Log & CMD Log
ip_log = False
err_log = False
cmd_log = False
ip_info_log = False
abuseipdb_report = False

# File location.
ip_log_file = f'{output_log_path}/ip.log'
err_log_file = f'{output_log_path}/err.log'
cmd_log_file = f'{output_log_path}/cmd.log'
event_log_file = f'{output_log_path}/event.log'
ipinfo_log_file = f'{output_log_path}/ipinfo.log'
token_file = '.token'

# Find any args in command
if "ip" in sys.argv:
    ip_log = True
if "ipinfo" in sys.argv:
    ip_log = True
    ip_info_log = True
if "err" in sys.argv:
    err_log = True 
if "cmd" in sys.argv:
    cmd_log = True

if not os.path.exists(output_log_path):
    os.system(f"mkdir {output_log_path}")

# Logging config
logging.basicConfig(
    filename=err_log_file,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Very ugly way to get screen size to integer
row, col = os.popen('stty size', 'r').read().strip().split()
x = int(col)

def getUserInput(prompt):
    while True:
        response = input(prompt).lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def getToken():
    with open(token_file, 'r') as tokenfile:
        for line in tokenfile:
            key, value = line.strip().split('=')
            if value:
                tokens[key] = value

# Universal clrscr
def clearScreen():
    os.system("cls" if os.name == "nt" else "clear")

# Display
## eventDisplay, cmdDisplay

def display(*args):
    if len(args) == 3:
        return f"{a.ljust(int(x/4))}CMD:{b.ljust(int(x/2)-4)}{c.ljust(int(x/4))}"
    elif len(args) == 4:
        return f"{a.ljust(int(x/4))}{b.ljust(int(x/4))}{c.ljust(int(x/4))}{d.ljust(int(x/4))}"
    else:
        return "Something Wrong."

# Function to process the events
def processLine(line):
    try:
        event = json.loads(line.strip())  # Parse JSON from the line

        # Extract username/password/cmd/src_ip/timestamps
        if event.get("eventid") in ["cowrie.login.success", "cowrie.login.failed"]:
            timestamp = datetime.strptime(event.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            username = event.get("username")
            password = event.get("password")
            src_ip = event.get("src_ip")

            if username:
                print(display(timestamp, username, password, src_ip))

            # IP Logging
            if ip_log:
                with open(ip_log_file, "a+") as iplog:
                    iplog.seek(0)
                    if event.get("src_ip") not in iplog.read():
                        iplog.write(f"{event.get('src_ip')}\n")
            
            # IP Info Logging
            if ip_info_log:
                # Check !isExist or !isEmpty
                if not os.path.exists(ipinfo_log_file) or os.stat(ipinfo_log_file).st_size == 0:
                    # Initialize file with new JSON obj
                    new_ip_data = getIPInfo(event.get("src_ip"))
                    if new_ip_data:
                        new_ip_data["count"] = 1

                        with open(ipinfo_log_file, "w") as ipinfolog:
                            json.dump([new_ip_data], ipinfolog, indent=4)
                else:
                    with open(ipinfo_log_file, "r+") as ipinfolog:
                        ip_data = json.load(ipinfolog)

                        # Attempts for each IP 
                        for entry in ip_data:
                            if entry["query"] == event.get("src_ip"):
                                entry["count"] += 1  # Increment count
                                break
                        else:
                            # IP not found, add new entry
                            new_ip_data = getIPInfo(event.get("src_ip"))
                            if new_ip_data:
                                new_ip_data["count"] = 1  # Initialize count
                                ip_data.append(new_ip_data)

                        # Write back to file
                        ipinfolog.seek(0)
                        json.dump(ip_data, ipinfolog, indent=4)
                        ipinfolog.truncate()


            with open(event_log_file, "a") as eventlog:
                eventlog.write(f"{display(timestamp, username, password, src_ip)}\n")

        if event.get("eventid") in ["cowrie.command.input"]:
            timestamp = datetime.strptime(event.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            cmd = event.get("input")
            src_ip = event.get("src_ip")

            if cmd:
                print(display(timestamp, cmd, src_ip))

            # CMD Logging
            if cmd_log:
                with open(cmd_log_file, "a+") as cmdlog:
                    cmdlog.write(f"{timestamp} from {src_ip}: {cmd}\n")

    except Exception as e:
        # Error Logging
        if err_log:
            logging.error(f"Error occurred: {e}\n{traceback.format_exc()}")

# Function to watch the file for new lines
def watchFile():
    try:
        # Logrotation check
        while True:
            with open(cowrie_log_path, 'r') as f:
                # Move to the end of the file to watch for new lines
                f.seek(0, os.SEEK_END)
                current_inode = os.fstat(f.fileno()).st_ino
                # print(current_inode)
            
                while True:
                    # Read new lines
                    new_line = f.readline()
            
                    if new_line:
                        processLine(new_line)
                    else:
                        time.sleep(1)

                    try:
                        if os.stat(cowrie_log_path).st_ino != current_inode:
                            f.close()  # Close the old file
                            f = open(cowrie_log_path, 'r')
                            # Move to the end of the new file
                            f.seek(0, os.SEEK_END)
                            # Update the current inode
                            current_inode = os.fstat(f.fileno()).st_ino
                    except FileNotFoundError:
                        # Handle the case where the file might not exist temporarily
                        time.sleep(1)
            continue
    except Exception as e:
        if err_log:
            logging.error(f"Error occurred: {e}\n{traceback.format_exc()}")

def getIPInfo(ip):
    response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,city,isp,org,proxy,hosting,query")
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            return data
        elif tokens.get('IPINFO_TOKEN'):
            # Query limit reached
            ipinfo_token = tokens.get('IPINFO_TOKEN')
            response = requests.get(f"https://ipinfo.io/{ip}?token={ipinfo_token}")
            data = response.json()
            return data
        else:
            print("No Available Info Source.")
    else:
        return f"Error. Code:{response.status_code}"

# Main
# Arg validating
if len(sys.argv) == 1:
    # If no arg is specified, do setup.
    ip_log = getUserInput("Do you want to log connected IP? (y/n)")
    ip_info_log = getUserInput("Do you want to log info of connected IP using ipinfo.io & ip-api.com API? (y/n)")
    err_log = getUserInput("Do you want to log error? (y/n)")
    cmd_log = getUserInput("Do you want to log commands from success connection? (y/n)")

elif len(sys.argv) > 5 or any(arg not in ["ip", "err", "cmd", "ipinfo"] for arg in sys.argv[1:]):
    # Invalid arg
    print("Usage: python main.py ip err cmd")
    print("ip: IP Logging")
    print("err: Error Logging")
    print("cmd: Malicous CMD Logging")
    print("ipinfo: IP Info Logging (Also enable IP Logging)")
    sys.exit(1)
else:
    pass

clearScreen()

while True:
    cowrie_log_path = input("Cowrie JSON Location? Enter for default. (Default: ./cowrie.json)\n").strip()
    if not cowrie_log_path:
        cowrie_log_path = "./cowrie.json"
    if os.path.exists(cowrie_log_path):
        break
    clearScreen()
    print("Invalid Cowrie JSON file.")

clearScreen()

# Start watching the file
print(f"[Settings] IP Logging = {ip_log}")
print(f"[Settings] Error Logging = {err_log}")
print(f"[Settings] Malicous CMD Logging = {cmd_log}")
print(f"[Settings] IP Info Logging = {ip_info_log}")
print(f"Watching {cowrie_log_path} for new log entries...")
print(f"{'Timestamp':<{int(x/4)}}{'Username':<{int(x/4)}}{'Password':<{int(x/4)}}{'IP Address':<{int(x/4)}}")

# Keyboard Interupt 
try:
    os.system('stty -echo')
    getToken()
    watchFile()
except KeyboardInterrupt:
    os.system('stty echo')
    print("\nStopped file monitoring.")