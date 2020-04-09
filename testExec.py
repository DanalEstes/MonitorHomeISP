#!/usr/bin/env python3
# Python Script to invoke various network monitoring tools on a timer driven
# basis and send results to a POSIX queue for inclusion in a database. 
#
#
# Copyright (C) 2020 Danal Estes all rights reserved.
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
#

import subprocess
import sys
import argparse
import time
import os
import posix_ipc as ipc
import json
import re

# Globals.

###########################
# Methods begin here
###########################

def init():
    openQueue()
    print('Test Execution daemon - Initialization Complete.')

def openQueue():
	# Open, or create, the Queue that leads to the Database. 
	global queue
	queue=ipc.MessageQueue('/netmToDB', flags=ipc.O_CREAT, )


def getIP(netns):
    cmd  = 'ip -n '+netns+' address list'
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    outp = proc.stdout.readlines()    
    try: 
        line = str([line for line in outp if 'inet ' in str(line)][0])
        ip   = re.search(r'([\d.]+)',line).group(0)
    except:
        ip = ''
    if (len(ip) < 7):
        print('Failure to locate IP addressed adapters in netns '+netns)
        exit(8)
    return(ip)

def pingGoogle():
    ip = '8.8.4.4'
    cmd='ping -c 2 '+ip+' > /dev/null 2>&1'
    rc=subprocess.call(cmd, shell=True)
    print('Writing ping to queue ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    queue.send(json.dumps({'mtype':'testExecPing','mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),'mdict':{'status':rc,'ip':ip}}))


def speedTest():
    cmd='speedtest --json'
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    try:
        mdict = json.loads(proc.stdout.readline())
    except:
        mdict = {'download':0, 'upload':0}
    print('Writing speedtest to queue ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    queue.send(json.dumps({'mtype':'testExecSpeedTest','mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),'mdict':mdict})) 
    return()

def iperf3(interface,ip):
    cmd = 'iperf3 -J -B '+interface+' -c '+ip
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    outd = json.loads(proc.stdout.read())
    print('Writing iperf3 for ip '+ip+' to queue '+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    try:
        mdict = {'ip':ip,'rbps':outd['end']['sum_received']['bits_per_second']}
    except:
        mdict = {'ip':ip,'rbps':0}
    queue.send(json.dumps({'mtype':'testExecIperf3', \
        'mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()), \
        'mdict':mdict}))
    return()

def dig(host,dns):
    cmd = 'dig @'+dns+' '+host
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    outp = proc.stdout.readlines()
    mdict={'host':host,'dns':dns}
    for line in outp:
        line = str(line)
        if ('timed out' in line): mdict['QueryTime'] = 999
        if ('Query time' in line): mdict['QueryTime'] = [int(s) for s in line.split() if s.isdigit()][0]
    print('Writing Dig statistics for host '+host+' and dns '+dns+' to queue '+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    queue.send(json.dumps({'mtype':'testExecDig', \
        'mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()), \
        'mdict':mdict}))
    return()

###########################
# Main code begins here
###########################
init()

IPeth0 = getIP('if_lan')
IP2GHz = getIP('if_2GHz')
#IP5GHz = getIP('')  # How to access the root netns????
IPdotOne = re.search(r'([\d]+\.[\d]+\.[\d]+\.)',IPeth0).group(0)+'1'

prior01min = 0
prior05min = 0
prior15min = 0
prior60min = 0
while(1):
    global queue
    time.sleep(10)
    tnow = int(time.time())
    if ((tnow - prior01min) > 59):  # One minute tests.
        pingGoogle()
        prior01min = tnow

    if ((tnow - prior15min) > 900):  # Fifteen minute tests.
        speedTest()
        iperf3(IPeth0, IP2GHz)
        iperf3(IPeth0, '192.168.7.245')
        dig('www.google.com',IPdotOne)
        dig('www.google.com','8.8.4.4')
        prior15min = tnow

    if ((tnow - prior60min) > 3600): # One Hour tests
        #speedTest()
        prior60min = tnow
