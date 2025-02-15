import jsonlines
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

input_file = ""
output_file = "./filtered.json"

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.last_position = 0  # Keeps track of where we left off

    def on_modified(self, event):
        """Triggered when the file is modified (new log entry added)."""
        if event.src_path == self.input_file:
            self.process_new_entries()

    def process_new_entries(self):
        """Reads new entries from the file and filters them."""
        with open(self.input_file, "r") as infile:
            infile.seek(self.last_position)  # Move to last read position
            with jsonlines.open(self.output_file, "a") as writer:  # Append mode
                for line in infile:
                    try:
                        json_obj = jsonlines.Reader([line]).read()  # Parse JSON
                        if json_obj.get("eventid", "") in ["cowrie.login.success", "cowrie.login.failed"]:
                            json_out = f"{json_obj.get('username', '').ljust(20)}{' ' * 10}{json_obj.get('password', '').ljust(30)}{' ' * 10}{json_obj.get('src_ip', '').ljust(20)}"
                            print(json_out)
                            writer.write(json_obj)  # Write filtered event
                    except Exception as e:
                        # print(f"Skipping malformed line: {e}")
                        continue
            self.last_position = infile.tell()  # Update last position

os.system("clear")
while True:
    input_file = str(input("Cowrie JSON Location?\n"))
    if os.path.exists(input_file):
        break
    os.system("clear")
    print("Invalid Cowrie JSON file.")

os.system("clear")
# Setup Watchdog Observer
event_handler = LogFileHandler(input_file, output_file)
observer = Observer()
observer.schedule(event_handler, ".", recursive=False)  # Watch current directory
observer.start()

print(f"Watching {input_file} for new log entries...")
print(f"{'Username':<30}{'Password':<40}{'IP Address':<30}")
try:
    while True:
        time.sleep(1)  # Keep script running
except KeyboardInterrupt:
    observer.stop()
    print("Stopped file monitoring.")

observer.join()
