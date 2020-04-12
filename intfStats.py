#!/usr/bin/env python3
# Python Script to take capture byte counts on interfaces via /sys/class/net/eth0 wlan0
# and similar. 
#
# Auto-discovers interfaces, and statistics. 
#
# Reads byte counts on a configurable interval, default every 0.5 second, because they are 
# 32 bit numbers that can rollover twice in a short period of time on a busy system.
# 
# Sends statistics over a POSIX queue to another daemon for application to a DB. Configurable
# interval, default 60 seconds. 
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
oldtime  = time.time()
intfStatOld = {}
intfStatAcc = {}

###########################
# Methods begin here
###########################

def init():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Captures network interfase stats to sqlite db.')
    parser.add_argument('-intfsec',type=float,nargs=1,default=[10])
    parser.add_argument('-datasec',type=float,nargs=1,default=[90])
    args=vars(parser.parse_args())
    global intfsec, datasec	
    intfsec  = args['intfsec'][0]
    datasec  = args['datasec'][0]
    findIntf()
    openQueue()
    print('Interface Statistic Capture - Initialization Complete.')

def findIntf():
    # Find all the interfaces, ignore lo (loopback).
    global intfStatOld, intfStatAcc
    proc = subprocess.Popen('ifconfig', shell=True,stdout=subprocess.PIPE)
    outd = proc.stdout.read().decode()
    dir  = re.findall('(^\w*?):',outd,re.M)
    try:
        dir.remove('lo:')
    except: 
        None

    for intf in dir:
        stats = ['tx_bytes','rx_bytes']
        intfStatOld[intf] = dict((n,0) for n in stats)
        intfStatAcc[intf] = dict((n,0) for n in stats)
        intfStatOld[intf]['seconds'] = time.time()

def accumStats():
    global intfStatOld, intfStatAcc
    for intf in intfStatAcc:
        proc = subprocess.Popen('ifconfig '+intf, shell=True,stdout=subprocess.PIPE)
        outd = proc.stdout.read().decode()
        tx_bytes = -1
        rx_bytes = -1
        try:
            rx_bytes = int(re.search('RX packets .*?bytes (\d+?) ',outd).group(1))
            tx_bytes = int(re.search('TX packets .*?bytes (\d+?) ',outd).group(1))
        except:
            None

        if (rx_bytes < intfStatOld[intf]['rx_bytes']     ): rx_bytes += 0xFFFFFFFF            
        if (not   intfStatOld[intf]['rx_bytes'] == 0): intfStatAcc[intf]['rx_bytes'] = intfStatAcc[intf]['rx_bytes'] + (rx_bytes - intfStatOld[intf]['rx_bytes'])
        intfStatOld[intf]['rx_bytes'] = rx_bytes

        if (tx_bytes < intfStatOld[intf]['tx_bytes']     ): tx_bytes += 0xFFFFFFFF            
        if (not   intfStatOld[intf]['tx_bytes'] == 0): intfStatAcc[intf]['tx_bytes'] = intfStatAcc[intf]['tx_bytes'] + (tx_bytes - intfStatOld[intf]['tx_bytes'])
        intfStatOld[intf]['tx_bytes'] = tx_bytes

def openQueue():
    # Open, or create, the Queue that leads to the Database. 
    global queue
    queue=ipc.MessageQueue('/netmToDB', flags=ipc.O_CREAT, )

###########################
# Main code begins here
###########################

init()

while(1):
    time.sleep(intfsec)
    accumStats()
    if (datasec < time.time() - oldtime):
        global queue
        for intf in intfStatAcc:
            print("Writing to DB Queue. "+intf,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()), flush=True)
            intfDict = intfStatAcc[intf]
            intfDict['intfName'] = intf
            intfDict['seconds']  = time.time() - intfStatOld[intf]['seconds'] 
            queue.send(json.dumps({'mtype':'intfStats','mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),'mdict':intfDict})) 
        oldtime = time.time()
        findIntf()
