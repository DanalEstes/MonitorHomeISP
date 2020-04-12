#!/usr/bin/env python3
# Python Script to check if a 'MontorHomeISP' system is 
# properly running. 
#

import subprocess
import posix_ipc as ipc

errorMsgs=[]

# The important part of this method is updating the error message array
def checkFor(output,check1,check2):
	global errorMsgs
	lines = [line for line in output if check1 in str(line)]

	if ((len(lines) > 0) and (not check2 == '')):
		lines = [line for line in output if check2 in str(line)]

	if (len(lines) > 0):
		return(0)

	global errorMsgs
	errorMsgs.append('MonitorHomeISP health check FAIL: >>>>> Missing or incorrect: '+check1+' '+check2+' <<<<< FAIL')

def runCmd(cmd):
	proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
	ps = proc.stdout.readlines()
	return(ps)

def checkSection(msg):
	global errorMsgs
	if (0 == len(errorMsgs)):
		print('MonitorHomeISP health check PASS: '+msg)
	else:
		print('MonitorHomeISP health check FAIL: >>>>> '+msg+' <<<<< FAIL  Details of failure:')
		[print(line) for line in errorMsgs]
		errorMsgs = []

######
### Main starts here
######

ps = runCmd('ip netns list')
checkFor(ps,'if_bridge', '')
checkFor(ps,'if_lan',    '')
checkFor(ps,'if_5GHz',   '')
checkFor(ps,'if_2GHz',   '')
checkSection('Network Name Spaces are correctly defined.')

ps = runCmd('ps -ef')
checkFor(ps,'testExec.py',     '')
checkFor(ps,'queueRecvDB.py',  '')
checkFor(ps,'intfStats.py',    '')
checkFor(ps,'iperf3',          '192.168.7.245')
checkFor(ps,'iperf3',          '192.168.7.242')
checkSection('Daemons processes found and appear healthy.')

ps = runCmd('ip link list')
checkFor(ps,'wusb0','')
ps = runCmd('sudo ip netns exec if_2GHz ip link list')
checkFor(ps,'wbin0','')
ps = runCmd('sudo ip netns exec if_lan ip link list')
checkFor(ps,'eth0','')
checkSection('Layer 3 Links are defined correctly, and in the correct netns.')

ps = runCmd('ip link list')
checkFor(ps,'wusb0',  'UP')
ps = runCmd('sudo ip netns exec if_2GHz ip link list')
checkFor(ps,'wbin0',  'UP')
ps = runCmd('sudo ip netns exec if_lan ip link list')
checkFor(ps,'eth0',  'UP')
checkSection('Layer 3 Links are up and running and healthy.')

ps = runCmd('sudo ip netns exec if_bridge ip link list')
checkFor(ps,'br0','')
checkFor(ps,'eth1','')
checkFor(ps,'eth2','')
checkSection('Layer 2 Links are defined correctly, and in the correct netns.')
checkFor(ps,'br0',  'LOWER_UP')
checkFor(ps,'eth1', 'LOWER_UP')
checkFor(ps,'eth2', 'LOWER_UP')
checkSection('Layer 2 Links are up and running and healthy.')

# No underlying command for this one, so the flags in the
# runCmd and checkFor must be set manually. 
try:
	queue=ipc.MessageQueue('/netmToDB')
	if (queue.current_messages > 6):
		errorMsgs.append('MonitorHomeISP health check FAIL: Queue depth = '+str(queue.current_messages))
except: 		
	errorMsgs.append('MonitorHomeISP health check FAIL: Queue does not exist or this task does not have permissions.')
checkSection('Message queue is healthy.')

