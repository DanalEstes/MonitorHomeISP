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



def pingGoogle():
    ip = '8.8.4.4'
    cmd='ping -c 2 '+ip+' > /dev/null 2>&1'
    rc=subprocess.call(cmd, shell=True)
    print('Writing ping to queue ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    queue.send(json.dumps({'mtype':'testExecPing','mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),'mdict':{'status':rc,'ip':ip}}))


def speedTest():
    cmd='speedtest --json'
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    mdict = json.loads(proc.stdout.readline())
    print('Writing speedtest to queue ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    queue.send(json.dumps({'mtype':'testExecSpeedTest','mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),'mdict':mdict})) 
    return()

def iperf3(interface,ip):
    cmd = 'iperf3 -J -B '+interface+' -c '+ip
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    outd = json.loads(proc.stdout.read())
    print('Writing iperf3 for ip '+ip+' to queue '+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    try:
        queue.send(json.dumps({'mtype':'testExecIperf3', \
            'mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()), \
            'mdict':{'ip':ip,'rbps':outd['end']['sum_received']['bits_per_second']} \
            }))
    except:
        print('Queue command failed; often this means response from iperf3 did not contain proper "end" section.')
        print(outd)
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
        iperf3('192.168.7.240','192.168.7.242')
        iperf3('192.168.7.240','192.168.7.245')
        dig('www.google.com','192.168.7.1')
        dig('www.google.com','8.8.4.4')
        prior15min = tnow

    if ((tnow - prior60min) > 3600): # One Hour tests
        #speedTest()
        prior60min = tnow
