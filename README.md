# MonitorHomeISP

Pi based device to monitor and report on a typical home or SOHO internet connection. 

# Inspiration from mr_canoehead on reddit
Around April of 2020, mr_canoehead posted on reddit regarding a Pi based monitor that inspired me to write this one. 

He posted some details including logical and physical diagrams, lists of adapters, and and sample reports.  He did not post any code or detailed configurations.  His reddit thread was picked up and reblogged by Tom's Hardware and Google News, among others. Original reddit threads 
[here](https://www.reddit.com/r/raspberry_pi/comments/fqs1fj/a_network_performance_monitor_for_my_home_network/ "reddit/r/raspberry_pi")
and
[here](https://old.reddit.com/r/linux/comments/fq4s49/having_some_fun_with_network_namespaces_built_a/ "reddit/r/linux").

In short, the core ideas for this monitor are directly inspired by mr_canoehead's posts, and I owe him a great debt for his creativity.

All code is mine, and is release under the MIT license. 

## Status

At this moment, this is in ALPHA status. 

There is an install checklist; it is NOT a detailed, step-by-step, hold your hand, "click here" procedure. Not. 

You will need at least basic Linux or Raspberry Pi skills, comfortable at the command line, to install and use. Roughly, you will need to be very comfortable with navigating directories and copying files, editing files with nano or vi, sudo and when to use it, and be comfortable rebooting the pi about a million times. 

## Support
NONE at this time. 

Feel free to experiment; I will not be taking issues or pulls, or etc, until such time as I harden this up quite a bit.  Come back often and look for commits as I get this running more smoothly.  On the other hand, if you have ideas for things it should be doing, that you just don't quiet know how to code, please feel free to make a suggestion via email. 

## Hardware
This hardware combination seems to run with medium term (several hours) stability.  Will report back if long term stable. 

Pi4s seem to have lots of heat problems.  I have a couple of big heatsinks on order.  I will update as soon as I find something effective and fanless. 

* Raspberry Pi 4b with 2Gig (or more) of ram.  Example at [Amazon](https://www.amazon.com/gp/product/B07V2B4W63).  There are plenty of other sources.
(https://www.amazon.com/gp/product/B01N9M32TA)~~
* TP-Link USB to Ethernet Adapter (TL-UE300) [Amazon](https://www.amazon.com/gp/product/B00YUU3KC6) -  Two of these.
* TP-Link USB Wifi Adapter for PC AC600Mbps Wireless Network Adapter (this may change) [Amazon](https://www.amazon.com/gp/product/B07P5PRK7J)
* TP-Link AC1300 - USB 3.0 Mini WiFi Adapter [Amazon](https://www.amazon.com/gp/product/B07P6N2TZH) - I haven't received one of these yet, and they appear to have gone out of stock.  So this may or may not be an alternative. 

## Software
* Raspbian image (current from raspberrypi.org)  Get the "with desktop", the middle one. 
* Other software detailed in installation checklist. All installed with apt or pip

## Installation
Follow the steps in [install.txt](https://github.com/DanalEstes/MonitorHomeISP/blob/master/install.txt)

