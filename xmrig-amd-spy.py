import requests
import json
import os
import sys
import psutil
import signal
import time
import datetime
import subprocess
from slackclient import SlackClient
from datetime import datetime

BoxName='MyAwesomeBox'
MinerFolder = 'C:\\Users\\Username\\Desktop\\Miner\\xmrig-amd'
MinerCommand = 'xmrig-amd.exe --api-port 8181 -o xmr-eu2.nanopool.org:14444 -u mywallet-address --donate-level=\"1\%\"'
MinerRemoteAddress = 'http://127.0.0.1:8181'

MinHashRate = "8400";

# You need to download and setup OverdriveNTool
# the example is for 6 RXVega56 and using OverdriveNTool configuration file: Vega56N
OverDriveFolder = 'C:\\Users\\Username\\Desktop\\Miner'
OverDriveCommand = 'OverdriveNTool.exe -r1 -r2 -r3 -r4 -r5 -r6 -p1Vega56N -p2Vega56N -p3Vega56N -p4Vega56N -p5Vega56N -p6Vega56N'

# You need to download and install WinAMDTweak
# This example timer is based on Sapphire RXVega56 Nitro+ Hynix Memory, soft PP table and set at 1480/815, 860/815, power -20%
MemTweakFolder = 'C:\\Users\Username\Desktop\Miner'
MemTweakCommand = 'WinAMDTweak.exe --rcdrd 19 --rcdwr 4 --rc 35 --rp 14 --rrds 4 --rrdl 5 --rfc 148 --REF 15600'

SlackUser="slack_username"
SlackChannel="#slack_channel"
SlackToken="slack_token"

'''
    Applying GPU settings, Currently only applying OverDrive Tools.
    If you are using AMD BlockChain Driver, you might need to add restart GPU here
'''
def applySettings():
    print 'Applying GPU settings'
    
    sendSlack('%s applying GPU settings' % (BoxName))
    subprocess.Popen('%s\%s' % (OverDriveFolder, OverDriveCommand), cwd=OverDriveFolder)
    
    print 'Applying GPU memory strap'
    sendSlack('%s applying GPU memory tweak settings' % (BoxName))
    subprocess.Popen('%s\%s' % (MemTweakFolder, MemTweakCommand), cwd=MemTweakFolder, shell=True)
    
    return True


'''
    Starting Miner
'''
def startMiner():
    env = os.environ.copy()
    
    #python env wants string instead of int!
    env['GPU_FORCE_64BIT_PTR'] = '1'
    env['GPU_MAX_HEAP_SIZE'] = '100'
    env['GPU_USE_SYNC_OBJECTS'] = '1'
    env['GPU_MAX_ALLOC_PERCENT'] = '100'
    env['GPU_SINGLE_ALLOC_PERCENT'] = '100'
    
    environment = env
    print 'Starting XMRig instance'
    sendSlack('%s Starting Miner Instance' % (BoxName))
    return subprocess.Popen('%s\%s' % (MinerFolder, MinerCommand), env=environment, cwd=MinerFolder)


'''
    Killing miner using psutil
'''
def killMiner():
    print 'Stoping XMRig'
    sendSlack('%s Stopping Miner Instance' % (BoxName))
    for proc in psutil.process_iter():
        if proc.name() == "xmrig-amd.exe":
            proc.kill()


'''
    Sending message to slack
'''
def sendSlack(message):
    if message:
        try:
            s = SlackClient(SlackToken)
            output = "[{0}] {1}".format(datetime.now().strftime('%m-%d %H:%M'), message)
            s.api_call(
                 "chat.postMessage",
                 channel=SlackChannel,
                 text=output
             )
        except:
            pass


'''
    Restarting miner instance
'''
def restart():
    killMiner()
    applySettings()
    startMiner()
    


'''
    Stopping miner instance
'''
def shutdown(signal, number):
    killMiner()


'''
    Rebooting machine
'''
def reboot():
    killMiner()
    #subprocess.call(["shutdown", "/r", "/t", "5"])
    sys.exit()
    

'''
    Main Loop
'''
def main():
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    minute    = 0
    shares    = 0
    restarted = 0
    
    restart()
    while True:
        time.sleep(2)
        if restarted > 5:
            sendSlack('Rebooting box because failed to initialize miner or gpu properly')
            reboot()
          
        try:
            request = requests.get(MinerRemoteAddress)
            if not request.status_code or request.status_code is not 200:
                sendSlack('Restarting miner because failed to connect to miner properly')
                restarted += 1
                restart()
            else:
                break

        except Exception as e:
            sendSlack('Restarting miner due to error: %s' % (str(e)))
            restarted += 1
            restart()
    
    time.sleep(30)
    
    while True:
        try:
            request = requests.get(MinerRemoteAddress)
            if request.status_code is 200:               
                data = json.loads(request.text)
    
                # Check hashrate every 1 minute
                if data and data.get('hashrate', False) and data.get('hashrate').get('total'):
                    if int(MinHashRate) > int(data.get('hashrate').get('total')[0]):
                        sendSlack('Restarting miner due to low hashrate detected')
                        restart()

                # Check number of shares every 20 minutes
                minute = minute + 1
                if minute is 20:
                    if int(shares) == int(data['results']['shares_good']):
                        sendSlack('Restarting miner due to low shares detected')
                        restart()
                
                    else:
                        shares = data['results']['shares_good']
                        minute = 0;
                        

            if not request.status_code or request.status_code is not 200:
                sendSlack('Restarting miner due to invalid server request detected')
                restart()
            
            
        except Exception as e:
            sendSlack('Restarting miner due to error while spying: %s' % (str(e)))
            restart()
    

        time.sleep(60)


if __name__ == "__main__":
    main()
    
os.system('pause')
