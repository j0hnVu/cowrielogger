import json
import time
import os
import jsonlines
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.last_position = 0  # Last line worked on

    def on_modified(self, event):
        # Triggered when the file is modified (new log entry added).
        if event.src_path == self.input_file:
            self.process_new_entries()

    def process_new_entries(self):
        # Reads new entries from the file and filters them.
        try:
            with open(self.input_file, "r") as infile:
                # Check if the file has been truncated
                if os.path.getsize(self.input_file) < self.last_position:
                    print("File truncated. Resetting position.")
                    self.last_position = 0

                infile.seek(self.last_position)  # Move to last read position

                with jsonlines.open(self.output_file, "a") as writer:  # Append mode
                    for line in infile:
                        try:
                            json_obj = json.loads(line.strip())  # Parse JSON
                            if json_obj.get("eventid", "") in ["cowrie.login.success", "cowrie.login.failed"]:
                                timestamp = json_obj.get("timestamp", "")
                                try:
                                    formatted_time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    formatted_time = "Invalid Timestamp"

                                json_out = (
                                    f"{formatted_time.ljust(20)}{' ' * 10}"
                                    f"{json_obj.get('username', '').ljust(20)}{' ' * 10}"
                                    f"{json_obj.get('password', '').ljust(30)}{' ' * 10}"
                                    f"{json_obj.get('src_ip', '').ljust(20)}"
                                )
                                print(json_out)
                                writer.write(json_obj)  # Write filtered event
                        except json.JSONDecodeError as e:
                            # print(f"Skipping malformed line: {e}")
                            continue

                self.last_position = infile.tell()  # Update last position
        except Exception as e:
            print(f"Error processing file: {e}")


output_file = "./filtered.json"
clear_screen()

while True:
    input_file = input("Cowrie JSON Location?\n").strip()
    if os.path.exists(input_file):
        break
    clear_screen()
    print("Invalid Cowrie JSON file.")

clear_screen()

# Setup Watchdog Observer
event_handler = LogFileHandler(input_file, output_file)
observer = Observer()
observer.schedule(event_handler, path=os.path.dirname(input_file), recursive=False)
observer.start()

print(f"Watching {input_file} for new log entries...")
print(f"{'Timestamp':<30}{'Username':<30}{'Password':<40}{'IP Address':<30}")

try:
    while True:
        time.sleep(1)  # Keep script running
except KeyboardInterrupt:
    observer.stop()
    print("\nStopped file monitoring.")
observer.join()