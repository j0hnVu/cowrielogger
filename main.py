import json, time, os, logging, traceback, sys, requests
from datetime import datetime

# Initialize file_path
file_path = ''

# IP Log & Error Log & CMD Log
ip_log = False
err_log = False
cmd_log = False
ip_info_log = False

# Log file location.
ip_log_file = 'ip.log'
err_log_file = 'err.log'
cmd_log_file = 'cmd.log'
event_log_file = 'event.log'
ipinfo_log_file = 'ipinfo.log'

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


# Arg validating
if len(sys.argv) > 5 or any(arg not in ["ip", "err", "cmd", "ipinfo"] for arg in sys.argv[1:]):
    print("Usage: python main.py ip err cmd")
    print("ip: IP Logging")
    print("err: Error Logging")
    print("cmd: Malicous CMD Logging")
    print("ipinfo: IP Info Logging (Also enable IP Logging)")
    sys.exit(1)

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

# Universal clrscr
def clearScreen():
    os.system("cls" if os.name == "nt" else "clear")

# Display

## 4 vars
def eventDisplay(a, b, c, d):
    return f"{a.ljust(int(x/4))}{b.ljust(int(x/4))}{c.ljust(int(x/4))}{d.ljust(int(x/4))}"

## 3 vars
def cmdDisplay(a, b, c):
    return f"{a.ljust(int(x/4))}CMD:{b.ljust(int(x/2)-4)}{c.ljust(int(x/4))}"

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
                print(eventDisplay(timestamp, username, password, src_ip))

            # IP Logging
            if ip_log:
                with open(ip_log_file, "a+") as iplog:
                    iplog.seek(0)
                    if event.get("src_ip") not in iplog.read():
                        iplog.write(f"{event.get("src_ip")}\n")
            
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
                eventlog.write(f"{eventDisplay(timestamp, username, password, src_ip)}\n")

        if event.get("eventid") in ["cowrie.command.input"]:
            timestamp = datetime.strptime(event.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            cmd = event.get("input")
            src_ip = event.get("src_ip")

            if cmd:
                print(cmdDisplay(timestamp, cmd, src_ip))

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
            with open(file_path, 'r') as f:
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
                        if os.stat(file_path).st_ino != current_inode:
                            f.close()  # Close the old file
                            f = open(file_path, 'r')
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
        else:
            return f"Error: {data.get('message', 'Unknown error')}"


# Main
clearScreen()

while True:
    file_path = input("Cowrie JSON Location? (Default: ./cowrie.json\n").strip()
    if not file_path:
        file_path == "./cowrie.json"
    if os.path.exists(file_path):
        break
    clearScreen()
    print("Invalid Cowrie JSON file.")

clearScreen()

# Start watching the file
print(f"[Settings] IP Logging = {ip_log}")
print(f"[Settings] Error Logging = {err_log}")
print(f"[Settings] Malicous CMD Logging = {cmd_log}")
print(f"[Settings] IP Info Logging = {ip_info_log}")
print(f"Watching {file_path} for new log entries...")
print(f"{'Timestamp':<{int(x/4)}}{'Username':<{int(x/4)}}{'Password':<{int(x/4)}}{'IP Address':<{int(x/4)}}")

# Keyboard Interupt 
try:
    watchFile()
except KeyboardInterrupt:
    print("\nStopped file monitoring.")