import json
import time
import os
from datetime import datetime

# Path to your JSON file
file_path = './cowrie.json'

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Function to process the events
def process_line(line):
    event = json.loads(line.strip())  # Parse JSON from the line
    if event.get("eventid") in ["cowrie.login.success", "cowrie.login.failed"]:
        timestamp = datetime.strptime(event.get("timestamp"), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
        username = event.get("username")
        password = event.get("password")
        src_ip = event.get("src_ip")
        
        if username and src_ip:  # Ensure all fields exist
            print(f"{timestamp.ljust(20)}{' ' * 10}{username.ljust(20)}{' ' * 10}{password.ljust(30)}{' ' * 10}{src_ip.ljust(20)}")

# Function to watch the file for new lines
def watch_file():
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
print(f"{'Timestamp':<30}{'Username':<30}{'Password':<40}{'IP Address':<30}")
try:
    watch_file()
except KeyboardInterrupt:
    print("\nStopped file monitoring.")

