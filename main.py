import json, time, os, logging, traceback, sys
from datetime import datetime

# Path to your JSON file
file_path = ''

# IP Log & Error Log
ip_log = False
ip_log_file = 'ip.log'

err_log = False
err_log_file = 'err.log'

if "ip" in sys.argv:
    ip_log = True
if "err" in sys.argv:
    err_log = True 

if len(sys.argv) > 3 or sys.argv not in ["ip_log", "err_log"]:
    print("Usage: python main.py ip err")
    print("ip: IP Logging")
    print("err: Error Logging")
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
y = int(row)
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

        if event.get("eventid") in ["cowrie.command.input"]:
            timestamp = datetime.strptime(event.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            cmd = event.get("input")
            src_ip = event.get("src_ip")

            if cmd:
                cmd_display(timestamp, cmd, src_ip)

        if ip_log:
            with open(ip_log_file, "a+") as iplog:
                iplog.seek(0)
                if event.get("src_ip") not in iplog.read():
                    iplog.write(f"{event.get("src_ip")}\n")

    except Exception as e:
        if err_log:
            logging.error(f"Error occurred: {e}\n{traceback.format_exc()}")
        pass

# Function to watch the file for new lines
def watch_file():

    try:
        # Logrotation check
        ## Cowrie Logrotate use copy-truncate, so comparing inode won't work, so we compare file size instead.
        last_size = os.path.getsize(file_path)
        while True:
            with open(file_path, 'r') as f:
                # Move to the end of the file to watch for new lines
                f.seek(0, 2)
            
                while True:
                    # Read new lines
                    new_line = f.readline()
            
                    if new_line:
                        process_line(new_line)
                    else:
                        # Sleep for a short period before checking for new lines
                        time.sleep(1)

                    current_size = os.path.getsize(file_path)
                    if current_size < last_size:
                        break
    except Exception as e:
        if err_log:
            logging.error(f"Error occurred: {e}\n{traceback.format_exc()}")
        time.sleep(1)
        pass


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
print(f"Watching {file_path} for new log entries...")
print(f"{'Timestamp':<{int(x/4)}}{'Username':<{int(x/4)}}{'Password':<{int(x/4)}}{'IP Address':<{int(x/4)}}")
try:
    watch_file()
except KeyboardInterrupt:
    print("\nStopped file monitoring.")
