## Cowrie SSH Honeypot Logger

A Python script to monitor and display live SSH activity from a Cowrie honeypot log file (`cowrie.json`). Formats output for terminal readability.

## Features
- Real-time monitoring of SSH login attempts (success/failure) and executed commands

## Requirements
- Python 3.x
- Cowrie honeypot generating `cowrie.json` logs

## Usage
1. Run the script:
   ```bash
   python main.py
   ```

## Example Output
```
Watching /path/to/cowrie.json for new log entries...
Timestamp               Username           Password                   IP Address                    
2025-02-15 00:58:01     root               root                       192.168.1.1
2025-02-16 11:23:44     CMD:uname -m                                  192.168.1.1
```

## Notes
- Ensure that the cowrie.json log file **exists** before starting the script.

## Contribution
Contributions and modifications are welcome!

## Contact
**Email**: hoanganh170788@gmail.com
**Discord**: thatonempd
