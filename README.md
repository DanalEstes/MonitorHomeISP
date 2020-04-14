# MonitorHomeISP

Pi based device to monitor and report on a typical home or SOHO internet connection. 

Produces one of [these](https://github.com/DanalEstes/MonitorHomeISP/blob/master/dailyReport.pdf) every 24 hours (or when you trigger it). 


# Inspiration from mr_canoehead on reddit
Around April of 2020, mr_canoehead posted on reddit regarding a Pi based monitor that inspired me to write this one. 

He posted some details including logical and physical diagrams, lists of adapters, and and sample reports.  He did not post any code or detailed configurations.  His reddit thread was picked up and reblogged by Tom's Hardware and Google News, among others. Original reddit threads 
[here](https://www.reddit.com/r/raspberry_pi/comments/fqs1fj/a_network_performance_monitor_for_my_home_network/ "reddit/r/raspberry_pi")
and
[here](https://old.reddit.com/r/linux/comments/fq4s49/having_some_fun_with_network_namespaces_built_a/ "reddit/r/linux").

In short, the core ideas for this monitor are directly inspired by mr_canoehead's posts, and I owe him a great debt for his creativity.

All code is mine, and is release under the MIT license. 

## Status

At this moment, this is in ALPHA status; moveing to BETA 14 Apr 2020 (meaning I'm running it 'inline' at all times now).  

There is an install checklist; it is NOT a detailed, step-by-step, hold your hand, "click here" procedure. Not. 

You will need at least basic Linux or Raspberry Pi skills, comfortable at the command line, to install and use. Roughly, you will need to be very comfortable with navigating directories and copying files, editing files with nano or vi, sudo and when to use it, and be comfortable rebooting the pi about a million times. 

## Support
Open issues or pull requests.

Come back often and look for commits as I get this running more smoothly.  

## Hardware
This hardware combination runs stable for 48 hours or more: 

Pi4s seem to have lots of heat problems.  I have a couple of big heatsinks on order.  I will update as soon as I find something effective and fanless. Right now, running a fan. 

* Raspberry Pi 4b with 2Gig (or more) of ram.  Example at [Amazon](https://www.amazon.com/gp/product/B07V2B4W63).  There are plenty of other sources.
* TP-Link USB to Ethernet Adapter (TL-UE300) [Amazon](https://www.amazon.com/gp/product/B00YUU3KC6) -  Two of these.
* TP-Link USB Wifi Adapter for PC AC600Mbps Wireless Network Adapter (this may change) [Amazon](https://www.amazon.com/gp/product/B07P5PRK7J)

I am not running a USB3 hub; you may choose to do so.  Pick a simple, and robust, one. 

## Software
* Raspbian image (current from raspberrypi.org)  Get the "with desktop", the middle one. 
* Other software detailed in installation checklist. All installed with apt or pip

## Installation
Follow the steps in [install.txt](https://github.com/DanalEstes/MonitorHomeISP/blob/master/install.txt)

