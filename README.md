# Cowrie JSON Log Monitor

This script monitors a Cowrie honeypot JSON log file in real-time and extracts login events (`cowrie.login.success` and `cowrie.login.failed`). It filters these logs and saves them to `filtered.json` while displaying the extracted information in a structured format in the terminal.

## Features
- **Real-time monitoring**: Watches the specified Cowrie JSON log file for new entries.
- **Filters login events**: Extracts only `cowrie.login.success` and `cowrie.login.failed` events.
- **Formatted terminal output**: Displays Username, Password, and IP Address in aligned columns.
- **Appends filtered logs**: Saves extracted events to `filtered.json`.
- **Handles invalid JSON lines**: Skips malformed or incomplete entries.

## Requirements
Make sure you have Python installed along with the following dependencies:

```sh
pip install jsonlines watchdog
```

## Usage
1. **Run the script**:
   ```sh
   python script.py
   ```
2. **Enter the Cowrie JSON log file location** when prompted.
3. The script will start monitoring the file in real-time.
4. **Press `CTRL + C` to stop monitoring.**

## Example Output
```
Watching /path/to/cowrie.json for new log entries...
Timestamp                     Username                      Password                                IP Address                    
2025-02-15 00:58:01           root                          root                                    192.168.1.1
```

## Notes
- Ensure that the specified JSON log file **exists** before starting the script.
- The script clears the terminal before prompting for input and after confirming the file path.
- If an invalid file path is entered, it will prompt the user again until a valid path is provided.

## Contribution
Contributions and modifications are welcome!

