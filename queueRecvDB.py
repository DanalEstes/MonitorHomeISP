#!/usr/bin/env python3
# Python Script to read a queue of messages from other daemons and apply 
# statistics to a sqlite database. 
#
# Sent message types include:
#  intfStats frmo a custom Python dameon that reads eth0 wlan0 and similar statistics.
#  speedtest from speedtest-cli
#  more...
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
import sqlite3 as sql

# Globals.
createTableOnce = {}

###########################
# Methods begin here
###########################

def init():
    openQueue()
    openDB()
    print('Queue to DB daemon - Initialization Complete.')

def openQueue():
	# Open, or create, the Queue that leads to the Database. 
	global queue
	queue=ipc.MessageQueue('/netmToDB', flags=ipc.O_CREAT, )

def openDB():
    global dbConn
    dbConn = sql.connect('/home/pi/MonitorHomeISP/netm.db')
    global cur
    cur = dbConn.cursor()

def intfStatsToTable():
    global createTableOnce
    if (not 'intfStats' in createTableOnce):
        for intf in mdict:
            print('Creating intfStats table.')
            cmd = 'CREATE TABLE IF NOT EXISTS intfStats  '
            cmd += '(date string, intfName string, '
            print(mdict)
            for stat in mdict[intf]:
                cmd += stat+' int, '
            cmd = cmd[:-2]            
            cmd += ')'
            cur.execute(cmd)
            dbConn.commit()
            createTableOnce['intfStats'] = True
            break

    for intf in mdict:
        cmd = 'INSERT INTO intfStats  '
        cmd += '(date, intfName, '
        for stat in mdict[intf]:
            cmd += stat+', '
        cmd = cmd[:-2]            
        cmd += ") VALUES ('"+mtime+"', '"+intf+"', "
        for stat in mdict[intf]:
            cmd += str(mdict[intf][stat])+', '
        cmd = cmd[:-2]            
        cmd += ')'
        cur.execute(cmd)
        dbConn.commit()

def genericMsgToTable():
    global createTableOnce
    if (not mtype in createTableOnce):
        print('Creating table '+mtype)
        cmd = 'CREATE TABLE IF NOT EXISTS '+mtype
        cmd += ' (date string, '
        for key in mdict:
            cmd += key+' string, '
        cmd = cmd[:-2]            
        cmd += ')'
        cur.execute(cmd)
        dbConn.commit()
        createTableOnce[mtype] = True

    cmd = 'INSERT INTO '+mtype
    cmd += ' (date, '
    for key in mdict:
        cmd += key+', '
    cmd = cmd[:-2]            
    cmd += ") VALUES ('"+mtime+"', "
    for key in mdict:
        cmd += '"'+str(mdict[key])+'", '
    cmd = cmd[:-2]            
    cmd += ')'
    cur.execute(cmd)
    dbConn.commit()    



###########################
# Main code begins here
###########################

init()

while(1):
    global queue
    # This will be blocking if the Queue is empty. 
    message = queue.receive()[0]
    mlist   = json.loads(message) 
    mtype   = mlist['mtype']
    mtime   = mlist['mtime']
    mdict   = mlist['mdict']
    print('Queue message of type',mtype,'received',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),'with sent timestamp',mtime)
    if ('intfStats'         in mtype): genericMsgToTable()
    if ('testExecSpeedTest' in mtype): genericMsgToTable()
    if ('testExecPing'      in mtype): genericMsgToTable()
    if ('testExecIperf3'    in mtype): genericMsgToTable()
    if ('testExecDig'       in mtype): genericMsgToTable()

