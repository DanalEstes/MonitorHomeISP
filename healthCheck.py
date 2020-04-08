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

	if (not check2 == '' ):
		lines = [line for line in output if check2 in str(line)]

	if (len(lines) > 0):
		return(0)

	global errorMsgs
	errorMsgs.append('MonitorHomeISP health check FAIL: Missing or incorrect: '+check1+' '+check2)

def runCmd(cmd):
	proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
	ps = proc.stdout.read()
	ps = ps.splitlines()
	return(ps)

def checkSection(msg):
	global errorMsgs
	if (0 == len(errorMsgs)):
		print('MonitorHomeISP health check PASS: '+msg)
	else:
		[print(line) for line in errorMsgs]
		errorMsgs = []

######
### Main starts here
######

ps = runCmd('ip netns list')
checkFor(ps,'if_bridge', 'id: ')
checkFor(ps,'if_lan',    'id: ')
checkFor(ps,'if_5GHz',   'id: ')
checkFor(ps,'if_2GHz',   'id: ')
checkSection('Network Name Spaces are healthy.')

ps = runCmd('ps -ef')
checkFor(ps,'testExec.py',     '')
checkFor(ps,'queueRecvDB.py',  '')
checkFor(ps,'intfStats.py',    '')
checkFor(ps,'iperf3',          '192.168.7.245')
checkFor(ps,'iperf3',          '192.168.7.242')
checkSection('Daemons are healthy.')

ps = runCmd('ip link list')
checkFor(ps,'wusb0',  'UP')
ps = runCmd('sudo ip netns exec if_2GHz ip link list')
checkFor(ps,'wbin0',  'UP')
ps = runCmd('sudo ip netns exec if_lan ip link list')
checkFor(ps,'eth0',  'UP')
checkSection('IP Links are healthy.')
ps = runCmd('sudo ip netns exec if_bridge ip link list')
checkFor(ps,'br0',  'UP')
checkFor(ps,'eth1', 'UP')
checkFor(ps,'eth2', 'UP')
checkSection('Layer 2 Links are healthy.')

# No underlying command for this one, so the flags in the
# runCmd and checkFor must be set manually. 
try:
	queue=ipc.MessageQueue('/netmToDB')
	if (queue.current_messages > 6):
		errorMsgs.append('MonitorHomeISP health check FAIL: Queue depth = '+str(queue.current_messages))
except: 		
	errorMsgs.append('MonitorHomeISP health check FAIL: Queue does not exist or this task does not have permissions.')
checkSection('Message queue is healthy.')

