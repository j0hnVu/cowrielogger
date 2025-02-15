import jsonlines
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

input_file = "cowrie.json"  # Your JSON log file
output_file = "filtered.json"  # Output filtered file

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
                        if "cowrie.login" in json_obj.get("eventid", ""):
                            writer.write(json_obj)  # Write filtered event
                    except Exception as e:
                        print(f"Skipping malformed line: {e}")

            self.last_position = infile.tell()  # Update last position

# Setup Watchdog Observer
event_handler = LogFileHandler(input_file, output_file)
observer = Observer()
observer.schedule(event_handler, ".", recursive=False)  # Watch current directory
observer.start()

print(f"Watching {input_file} for new log entries...")
try:
    while True:
        time.sleep(1)  # Keep script running
except KeyboardInterrupt:
    observer.stop()
    print("Stopped file monitoring.")

observer.join()
