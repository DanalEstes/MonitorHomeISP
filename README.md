# MonitorHomeISP

Pi based device to monitor and report on a typical home or SOHO internet connection. 

# Inspiration from mr_canoehead on reddit
Around April of 2020, mr_canoehead posted a Pi based monitor that inspired me to write this one. 

He posted some details including logical and physical diagrams, lists of adapters, and similar.  He did not post any code or detailed configurations.  His reddit thread was picked up and reblogged by Tom's Hardware and Google News, among others. Original reddit threads 
[here](https://www.reddit.com/r/raspberry_pi/comments/fqs1fj/a_network_performance_monitor_for_my_home_network/ "reddit/r/raspberry_pi")
and
[here](https://old.reddit.com/r/linux/comments/fq4s49/having_some_fun_with_network_namespaces_built_a/ "reddit/r/linux").

The core ideas for this monitor are directly inspired by mr_canoeheads sample reports and other information.  All code is mine, and is release under the MIT license. 

## Status

At this moment, this is in ALPHA status.  There are no detailed, step-by-step, instructions. You will need at least basic Linux or Raspberry Pi skills, comfortable at the command line, to install and use. 

## Support
NONE at this time.  Feel free to experiment; I will not be taking issues or pulls, or etc, until such time as I harden this up quite a bit.  Come back often and look for commits. 

## Hardware
* Raspberry Pi 4b with 2Gig (or more) of ram.  Example at [Amazon](https://www.amazon.com/gp/product/B07V2B4W63).  There are plenty of other sources.
* TP-Link 3-Port USB 3.0 Portable USB Hub with 1 Gigabit Ethernet Port Network Adapter (UE330). [Amazon](https://www.amazon.com/gp/product/B01N9M32TA) 
* TP-Link USB to Ethernet Adapter (TL-UE300) [Amazon](https://www.amazon.com/gp/product/B00YUU3KC6)
* TP-Link USB Wifi Adapter for PC AC600Mbps Wireless Network Adapter (this may change) [Amazon](https://www.amazon.com/gp/product/B07P5PRK7J)
* TP-Link AC1300 - USB 3.0 Mini WiFi Adapter [Amazon](https://www.amazon.com/gp/product/B07P6N2TZH) - I haven't received one of these yet, and they appear to have gone out of stock.  So this may or may not be an alternative. 

## Software
* Raspbian image (current from raspberrypi.org)  Get the "with desktop", the middle one. 
* Other software detailed in installation checklist.

## Installation
Follow the steps in ...

