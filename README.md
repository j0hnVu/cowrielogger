## Cowrie SSH Honeypot Logger

A Python script to monitor and display live SSH activity from a Cowrie honeypot JSON log file. Formats output for terminal readability.

## Features
- Real-time monitoring of SSH login attempts (success/failure) and executed commands
- Output all malicious IPs and executed commands to log files for analysis
- Retrieve IP's info like country, region, ISP from ip.api.com

## Requirements
- Python 3.x
- Cowrie honeypot generating `cowrie.json` logs

## Usage
   ```bash
   git clone https://github.com/j0hnVu/cowrielogger.git
   cd cowrielogger
   python main.py ipinfo cmd err
   ```

   *ip*: IP Logging to ip.log

   *err*: Error Logging to err.log

   *cmd*: Executed command Logging to cmd.log

   *ipinfo*: IP Info Logging using ip-api.com API (This will also enable ip logging)

## Example Output

**Output:**
``` 
[Settings] IP Logging = True
[Settings] Error Logging = False
Watching /path/to/cowrie.json for new log entries...
Timestamp               Username           Password                   IP Address                    
2025-02-15 00:58:01     root               root                       192.168.1.1
2025-02-16 11:23:44     CMD:uname -m                                  192.168.1.1
```

**ip.log**
```
192.168.1.1
{'country': 'Some Country', 'region': 'Some Region', 'isp': 'Some ISP'}
```

**cmd.log**
```
2025-02-25 11:10:03 from 192.168.1.1: echo "Hello"
```


## Contribution
Contributions and modifications are welcome!

## Contact
**Email**: hoanganh170788@gmail.com

**Discord**: thatonempd
