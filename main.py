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
    print("Usage: python main.py ip err cmd ipinfo")
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
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Display

## 4 vars
def display(a, b, c, d):
    print(f"{a.ljust(int(x/4))}{b.ljust(int(x/4))}{c.ljust(int(x/4))}{d.ljust(int(x/4))}")

## 3 vars
def cmd_display(a, b, c):
    print(f"{a.ljust(int(x/4))}CMD:{b.ljust(int(x/2)-4)}{c.ljust(int(x/4))}")

# Function to process the events
def process_line(line):
    try:
        event = json.loads(line.strip())  # Parse JSON from the line

        # Extract username/password/cmd/src_ip/timestamps
        if event.get("eventid") in ["cowrie.login.success", "cowrie.login.failed"]:
            timestamp = datetime.strptime(event.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            username = event.get("username")
            password = event.get("password")
            src_ip = event.get("src_ip")

            if username:
                display(timestamp, username, password, src_ip)

            # IP Logging
            if ip_log:
                with open(ip_log_file, "a+") as iplog:
                    iplog.seek(0)
                    if event.get("src_ip") not in iplog.read():
                        iplog.write(f"{event.get("src_ip")}\n")
                        if ip_info_log:
                            iplog.write(f"{getIPInfo(event.get("src_ip"))}\n")

        if event.get("eventid") in ["cowrie.command.input"]:
            timestamp = datetime.strptime(event.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            cmd = event.get("input")
            src_ip = event.get("src_ip")

            if cmd:
                cmd_display(timestamp, cmd, src_ip)

            # CMD Logging
            if cmd_log:
                with open(cmd_log_file, "a+") as cmdlog:
                    cmdlog.write(f"{timestamp} from {src_ip}: {cmd}\n")

    except Exception as e:
        # Error Logging
        if err_log:
            logging.error(f"Error occurred: {e}\n{traceback.format_exc()}")
        pass

# Function to watch the file for new lines
def watch_file():
    try:
        # Logrotation check
        while True:
            with open(file_path, 'r') as f:
                # Move to the end of the file to watch for new lines
                f.seek(0, os.SEEK_END)
                current_inode = os.fstat(f.fileno()).st_ino
                print(current_inode)
            
                while True:
                    # Read new lines
                    new_line = f.readline()
            
                    if new_line:
                        process_line(new_line)
                    else:
                        time.sleep(1)

                    try:
                        if os.stat(file_path).st_ino != current_inode:
                            # Reopen the file with the new inode
                            with open(file_path, 'r') as new_f:
                                f.close()  # Close the old file
                                f = new_f
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
    response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,city,isp,org,proxy,hosting")
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            return response
        else:
            return f"Error: {data.get('message', 'Unknown error')}"


# Main
clear_screen()

while True:
    file_path = input("Cowrie JSON Location? (Default: ./cowrie.json\n").strip()
    if not file_path:
        file_path == "./cowrie.json"
    if os.path.exists(file_path):
        break
    clear_screen()
    print("Invalid Cowrie JSON file.")

clear_screen()

# Start watching the file
print(f"[Settings] IP Logging = {ip_log}")
print(f"[Settings] Error Logging = {err_log}")
print(f"[Settings] Malicous CMD Logging = {cmd_log}")
print(f"[Settings] IP Info Logging = {ip_info_log}")
print(f"Watching {file_path} for new log entries...")
print(f"{'Timestamp':<{int(x/4)}}{'Username':<{int(x/4)}}{'Password':<{int(x/4)}}{'IP Address':<{int(x/4)}}")

# Keyboard Interupt 
try:
    watch_file()
except KeyboardInterrupt:
    print("\nStopped file monitoring.")