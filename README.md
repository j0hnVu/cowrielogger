## Cowrie SSH Honeypot Logger

A Python script to monitor and display live SSH activity from a Cowrie honeypot log file. Formats output for terminal readability.

## Features
- Real-time monitoring of SSH login attempts (success/failure) and executed commands
- Output all malicious IPs and executed commands to log files for analysis

## Requirements
- Python 3.x
- Cowrie honeypot generating `cowrie.json` logs

## Usage
   ```bash
   git clone https://github.com/j0hnVu/cowrielogger.git
   touch ip.log err.log
   python main.py ip err
   ```

   *ip*: IP Logging to ip.log

   *err*: Error Logging to err.log

   *cmd*: Executed command Logging to cmd.log

## Example Output
```
[Settings] IP Logging = True
[Settings] Error Logging = False
Watching /path/to/cowrie.json for new log entries...
Timestamp               Username           Password                   IP Address                    
2025-02-15 00:58:01     root               root                       192.168.1.1
2025-02-16 11:23:44     CMD:uname -m                                  192.168.1.1
```

## Notes
- Ensure that the cowrie.json, ip.log, err.log log file **exists** before starting the script.

## Contribution
Contributions and modifications are welcome!

## Contact
**Email**: hoanganh170788@gmail.com
**Discord**: thatonempd
