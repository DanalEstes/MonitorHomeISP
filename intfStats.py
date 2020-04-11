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
    parser.add_argument('-intfsec',type=float,nargs=1,default=[2])
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
    dir = os.listdir('/sys/class/net/')
    dir.remove('lo')
    for intf in dir:
        dir = os.listdir('/sys/class/net/'+intf+'/statistics/')
        intfStatOld[intf] = dict((n,0) for n in dir)
        intfStatAcc[intf] = dict((n,0) for n in dir)
        intfStatOld[intf]['seconds'] = time.time()


def accumStats():
    global intfStatOld, intfStatAcc
    for intf in intfStatAcc:
        for stat in intfStatAcc[intf]:
            fn = '/sys/class/net/'+intf+'/statistics/'+stat
            with open (fn, 'r') as f: num = int(f.readlines()[0].rstrip())

            #if(('eth2' == intf) and ('tx_bytes' == stat)):
            #    print('num ', num, ' old ', intfStatOld[intf][stat], ' minus ', num - intfStatOld[intf][stat]  )
            if (num < intfStatOld[intf][stat]     ): num += 0xFFFFFFFF            
            if (not   intfStatOld[intf][stat] == 0): intfStatAcc[intf][stat] = intfStatAcc[intf][stat] + (num - intfStatOld[intf][stat])
            intfStatOld[intf][stat] = num

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
