#!/usr/bin/env python3
# Python Script to produce daily reports in the network monitoring system. 
#
#
# Copyright (C) 2020 Danal Estes all rights reserved.
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
#

import sqlite3 as sql
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import time
import datetime
import argparse


# Globals.
argYesterday = False


###########################
# Methods begin here
###########################
def init():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Program to create Daily Report from Database on Network Monitor Device.')
    parser.add_argument('-yesterday',action='store_true')
    args=vars(parser.parse_args())
    global yesterday
    yesterday     = args['yesterday']

def openDB():
    global dbConn
    dbConn = sql.connect('/home/pi/MonitorHomeISP/netm.db')
    global cur
    cur = dbConn.cursor()

def x10minDT():
    date = datetime.date.today() 
    if (yesterday): date += datetime.timedelta(-1)
    x = list(range(0, 24*60*60, 10*60))
    for i,t in enumerate(x):
        secs = time.mktime(date.timetuple())
        secs += t
        times = time.strftime('%Y-%m-%d %H:%M',time.localtime(secs))
        x[i]=times
    y = [None for i in x]
    return([x,y])

def smoothGaps(data):
    for i, val in enumerate(data):
        if (val is None):
            data[i] = data[i-1]
    return(data)

def plotPing():
    print('Plotting Ping basic Up/Down')
    global cur

    # Prototype the X and Y value lists
    x, y = x10minDT()
    # Change the default value to "unknown"
    y = [2 for i in y]

    # Calculate date ranges for DB read
    start = datetime.date.today() 
    if (yesterday): start += datetime.timedelta(-1)
    start = start.strftime('%Y-%m-%d 00:00:00')
    end   = datetime.date.today() 
    if (yesterday): end += datetime.timedelta(-1)
    end   = end.strftime('%Y-%m-%d 23:59:59')

    # Get DB data for those dates
    cmd = 'SELECT date, sum(status) from testExecPing '
    cmd += 'WHERE date > "'+start+'" and '+'date < "'+end+'" '
    cmd += 'GROUP BY substr(date,0,16)' # 14 = by hour, 16 = by 10 min
    cur.execute(cmd)
    rows = cur.fetchall()
    # Load DB data into prototyped X and Y value lists
    for row in rows:
        # Find the 10 minute bucket in which this fits. 
        secs = time.mktime(time.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
        base = time.mktime(time.strptime(row[0][0:10], '%Y-%m-%d'))
        i = int((secs-base)/(10*60)) 
        if ((i < 0) or (i > len(y))): 
            print('Y index screwed up somewhere!',i)
            next
        y[i] = 3 - (2 * (not row[1]<2))

    # Generate the plot
    fig, ax = plt.subplots(figsize=(10,4))
    ax.set_ylim([0.75, 3.25])
    plt.yticks([3, 2, 1], ['UP', 'UNKNOWN', 'DOWN' ])
    plt.plot(x,y)

    plt.grid(axis='x', linestyle='-', which='major')
    n=(int(len(x)/24))
    [l.set_visible(False) for (i,l) in enumerate(ax.xaxis.get_ticklabels()) if ((i % n) != 0)]

    fig.autofmt_xdate()

    plt.title('Internet Up/Down based on Ping of 8.8.4.4')
    plt.savefig('dailyReportPing.png', bbox_inches='tight')

def plotSpeedTest():
    print('Plotting Speed Tests')
    global cur

    # Prototype the X and Y value lists
    x, y1 = x10minDT()
    y2=y1.copy()

    # Calculate date ranges for DB read
    start = datetime.date.today() 
    if (yesterday): start += datetime.timedelta(-1)
    start = start.strftime('%Y-%m-%d 00:00:00')
    end   = datetime.date.today() 
    if (yesterday): end += datetime.timedelta(-1)
    end   = end.strftime('%Y-%m-%d 23:59:59')

    # Get DB data for those dates
    cmd = 'SELECT date, avg(download) as dn, avg(upload) as up FROM testExecSpeedTest '
    cmd += 'WHERE date > "'+start+'" and '+'date < "'+end+'" '
    cmd += 'GROUP BY substr(date,0,16)' # 14 = by hour, 16 = by 10 min
    cur.execute(cmd)

    # Load the data into the prototype value lists
    rows = cur.fetchall()
    for row in rows:
        # Find the 10 minute bucket in which this fits. 
        secs = time.mktime(time.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
        base = time.mktime(time.strptime(row[0][0:10], '%Y-%m-%d'))
        i = int((secs-base)/(10*60)) 
        if ((i < 0) or (i > len(y1))): 
            print('Y index screwed up somewhere!',i)
            next

        y1[i] = (row[1] / 1024 / 1024)  # bits per second / 1024 /1024 = Mbits/sec
        y2[i] = (row[2] / 1024 / 1024)  # bits per second / 1024 /1024 = Mbits/sec

    y1 = smoothGaps(y1)
    y2 = smoothGaps(y2)

    # Generate and save the plot. 
    fig, ax1 = plt.subplots(figsize=(12,5))
    ax1.set_ylim(50,150)
    ax1.set_ylabel('Download', color='tab:red')
    ax1.plot(x,y1, color='tab:red')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax2 = ax1.twinx()
    ax2.set_ylim(2,4)
    ax2.set_ylabel('Upload', color='tab:blue')
    ax2.plot(x,y2, color='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    ax1.grid(True, linestyle='-.')
    n=(int(len(x)/24))
    [l.set_visible(False) for (i,l) in enumerate(ax1.xaxis.get_ticklabels()) if ((i % n) != 0)]


    fig.autofmt_xdate()
    plt.title('SpeedTest download and upload speeds, Mbps, Direct Ethernet Connection')
    plt.savefig('dailyReportSpeedTest.png', bbox_inches='tight')

def plotIperf3():
    print('Plotting Iperf3 client tests')
    global cur

    cur.execute('select distinct ip from testExecIperf3')
    distinctIP = cur.fetchall()

    for ip in distinctIP:
        # Prototype the X and Y value lists
        x, y = x10minDT()

        # Calculate date ranges for DB read
        start = datetime.date.today() 
        if (yesterday): start += datetime.timedelta(-1)
        start = start.strftime('%Y-%m-%d 00:00:00')
        end   = datetime.date.today() 
        if (yesterday): end += datetime.timedelta(-1)
        end   = end.strftime('%Y-%m-%d 23:59:59')

        cmd = 'SELECT date, avg(rbps) from testExecIperf3 '
        cmd += 'WHERE date > "'+start+'" and '+'date < "'+end+'" and ip = "'+ip[0]+'" '
        cmd += 'GROUP BY substr(date,0,16)' # 14 = by hour, 16 = by 10 min
        cur.execute(cmd)
        rows = cur.fetchall()

        for row in rows:
            # Find the 10 minute bucket in which this fits. 
            secs = time.mktime(time.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            base = time.mktime(time.strptime(row[0][0:10], '%Y-%m-%d'))
            i = int((secs-base)/(10*60)) 
            if ((i < 0) or (i > len(y))): 
                print('Y index screwed up somewhere!',i)
                next

            y[i] = (row[1] / 1024 / 1024)  # bits per second / 1024 /1024 = Mbits/sec

        y = smoothGaps(y)    
        # Generate and save the plot
        fig, ax = plt.subplots(figsize=(10,4))
        ax.set_ylim(0,300)
        plt.plot(x,y)

        plt.grid(axis='x', linestyle='-')
        n=(int(len(x)/24))
        [l.set_visible(False) for (i,l) in enumerate(ax.xaxis.get_ticklabels()) if ((i % n) != 0)]

        fig.autofmt_xdate()

        plt.title('Iperf3 Bits Per Second to server at IP '+ip[0])
        plt.savefig('dailyReportIperf'+ip[0][-1]+'.png', bbox_inches='tight')

def plotDig():
    print('Plotting Dig (dns resolution) response time. ')
    global cur

    # Prototype the X and Y value lists
    x, y1 = x10minDT()
    y2=y1.copy()

    # Calculate date ranges for DB read
    start = datetime.date.today() 
    if (yesterday): start += datetime.timedelta(-1)
    start = start.strftime('%Y-%m-%d 00:00:00')
    end   = datetime.date.today() 
    if (yesterday): end += datetime.timedelta(-1)
    end   = end.strftime('%Y-%m-%d 23:59:59')

    # Get DB data for those dates
    #cmd = 'SELECT date, avg(QueryTime), dns FROM testExecDig '
    cmd = 'SELECT date, QueryTime, dns FROM testExecDig '
    cmd += 'WHERE date > "'+start+'" and '+'date < "'+end+'" '
    #cmd += 'GROUP BY substr(date,0,16)' # 14 = by hour, 16 = by 10 min
    cur.execute(cmd)

    # Load the data into the prototype value lists
    rows = cur.fetchall()
    for row in rows:
        # Find the 10 minute bucket in which this fits. 
        secs = time.mktime(time.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
        base = time.mktime(time.strptime(row[0][0:10], '%Y-%m-%d'))
        i = int((secs-base)/(10*60)) 
        if ((i < 0) or (i > len(y1))): 
            print('Y index screwed up somewhere!',i)
            next
        if ('192.168' in row[2]): y1[i] = (row[1] ) 
        if ('8.8'     in row[2]): y2[i] = (row[1] ) 

    y1 = smoothGaps(y1)
    y2 = smoothGaps(y2)

    # Generate and save the plot. 
    fig, ax1 = plt.subplots(figsize=(12,5))
    ax1.set_ylim(0,60)
    ax1.set_ylabel('192.168.7.1', color='tab:red')
    ax1.plot(x,y1, color='tab:red')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax2 = ax1.twinx()
    ax2.set_ylim(0,60)
    ax2.set_ylabel('8.8.4.4', color='tab:blue')
    ax2.plot(x,y2, color='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    ax1.grid(True, linestyle='-.')
    n=(int(len(x)/24))
    [l.set_visible(False) for (i,l) in enumerate(ax1.xaxis.get_ticklabels()) if ((i % n) != 0)]


    fig.autofmt_xdate()
    plt.title('DNS resolution in milleseconds; Local (ISP) and Google')
    plt.savefig('dailyReportDig.png', bbox_inches='tight')

def plotIntfStats():
    print('Plotting Interface Bit Per Second Rates.')
    global cur

    cur.execute('select distinct intfName from intfStats')
    distinctIntf = cur.fetchall()

    for intf in distinctIntf:
        # Prototype the X and Y value lists
        x, y1 = x10minDT()
        y2    = y1.copy()

        # Calculate date ranges for DB read
        start = datetime.date.today() 
        if (yesterday): start += datetime.timedelta(-1)
        start = start.strftime('%Y-%m-%d 00:00:00')
        end   = datetime.date.today() 
        if (yesterday): end += datetime.timedelta(-1)
        end   = end.strftime('%Y-%m-%d 23:59:59')

        #cmd = 'SELECT date, intfName, avg(tx_Bytes) as tx, avg(rx_Bytes) as rx from intfStats '
        cmd = 'SELECT date, intfName, tx_Bytes, rx_Bytes, seconds from intfStats '
        cmd += 'WHERE date > "'+start+'" and '+'date < "'+end+'" and intfName = "'+intf[0]+'" '
        #cmd += 'GROUP BY substr(date,0,16) ' # 14 = by hour, 16 = by 10 min
        cmd += 'ORDER BY date '
        cur.execute(cmd)
        rows = cur.fetchall()

        for row in rows:
            # Find the 10 minute bucket in which this fits. 
            secs = time.mktime(time.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            base = time.mktime(time.strptime(row[0][0:10], '%Y-%m-%d'))
            i = int((secs-base)/(10*60)) 
            if ((i < 0) or (i > len(y1))): 
                print('Y index screwed up somewhere!',i)
                next

            #y1[i] = ((row[2] * 8) / row[4] / 1024 / 1024)  # Bytes * 8 / seconds = bits per second / 1024 / 1024 = Mbits/sec
            mbps = ((row[2] * 8) / row[4] / 1024 / 1024)  # Bytes * 8 / seconds = bits per second / 1024 / 1024 = Mbits/sec
            if (y1[i]):
                y1[i] = max(y1[i], mbps) 
            else:
                y1[i] = mbps

            mbps = ((row[3] * 8) / row[4] / 1024 / 1024)  # Bytes * 8 / seconds = bits per second / 1024 / 1024 = Mbits/sec
            if (y2[i]):
                y2[i] = max(y2[i], mbps)
            else:
                y2[i] = mbps

        #y1 = smoothGaps(y1)    
        #y2 = smoothGaps(y2)    
        # Generate and save the plot
        fig, ax1 = plt.subplots(figsize=(10,4))
        ax1.set_ylim(0,50)
        ax1.set_ylabel('Transmitted Mb/s', color='tab:red')
        ax1.plot(x,y1, color='tab:red')
        ax1.tick_params(axis='y', labelcolor='tab:red')
        ax1.grid(axis='x', linestyle='-')

        ax2 = ax1.twinx()
        ax2.set_ylim(0,50)
        ax2.set_ylabel('Received Mb/s', color='tab:blue')
        ax2.plot(x,y2, color='tab:blue')
        ax2.tick_params(axis='y', labelcolor='tab:blue')

        n=(int(len(x)/24))
        #[l.set_visible(False) for (i,l) in enumerate(ax1.xaxis.get_ticklabels()) if ((i % n) != 0)]

        fig.autofmt_xdate()

        plt.title('MBits Per Second, 10 sec peak of each 10 min interval, interface '+intf[0])
        plt.savefig('dailyReportIntf'+intf[0]+'.png', bbox_inches='tight')


###########################
# Main code begins here
###########################
init()
openDB()
plotPing()
plotSpeedTest()
plotIperf3()
plotDig()
plotIntfStats()

subprocess.call('cd /home/pi/MonitorHomeISP && pdflatex dailyReport.tex -shell-escape', shell=True) 