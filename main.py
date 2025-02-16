import json
import time
import os
from datetime import datetime

# Path to your JSON file
file_path = './cowrie.json'
row, col = os.popen('stty size', 'r').read().strip().split()
y = int(row)
x = int(col)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display(a, b, c, d):
    print(f"{a.ljust(int(x/4))}{b.ljust(int(x/4))}{c.ljust(int(x/4))}{d.ljust(int(x/4))}")

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

            if username and src_ip:
                display(timestamp, username, password, src_ip)

        if event.get("eventid") in ["cowrie.command.input"]:
            timestamp = datetime.strptime(event.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            cmd = event.get("input")
            src_ip = event.get("src_ip")

            if cmd:
                cmd_display(timestamp, cmd, src_ip)
    except Exception as e:
        print(f"Err:{e}")    
        

# Function to watch the file for new lines
def watch_file():
    with open(file_path, 'r') as f:
        # Move to the end of the file to watch for new lines
        f.seek(0, 2)
        
        while True:
            # Read new lines
            new_line = f.readline()
            
            if new_line:
                try:
                    process_line(new_line)
                except Exception as e: # UnboundLocalError might happen here.
                    print(f"err:{e}")
            else:
                # Sleep for a short period before checking for new lines
                time.sleep(1)

# Main
clear_screen()

while True:
    file_path = input("Cowrie JSON Location?\n").strip()
    if os.path.exists(file_path):
        break
    clear_screen()
    print("Invalid Cowrie JSON file.")

clear_screen()

# Start watching the file
print(f"Watching {file_path} for new log entries...")
print(f"{'Timestamp':<{int(x/4)}}{'Username':<{int(x/4)}}{'Password':<{int(x/4)}}{'IP Address':<{int(x/4)}}")
try:
    watch_file()
except KeyboardInterrupt:
    print("\nStopped file monitoring.")
