Script for managing XMRig - AMD miner.
This script has the ability to auto restarting the XMRig - AMD miner when :
1. The hashrate falls below the configured amount
2. Low accepted share rate in certain duration
3. Not all GPU initialized properly
4. Script cannot contact miner via the port API

It has the ability to contact Slack and reports the status of the miner

Dependencies
1. Python 2.7
2. Python - SlackClient
3. Python - SlackUtil
4. XMRig-AMD
5. OverdriveNTool

Installation
1. Install python normally
2. Invoke :
    pip install psutil slackclient requests datetime
3. Configure the script
4. Run the script - if its ok, set it to auto run during boot time.
