# First, define the namespaces themselves
ip netns add if_2GHz
ip netns add if_5GHz
ip netns add if_lan
ip netns add if_bridge

# Then, move the interfaces in reverse order
# Second USB ether
ip link set eth2 netns if_bridge
# First USB ether
ip link set eth1 netns if_bridge
# Build the bridge
ip netns exec if_bridge brctl addbr br0
ip netns exec if_bridge brctl addif br0 eth2
ip netns exec if_bridge brctl addif br0 eth1
ip netns exec if_bridge ip link set eth1 up
ip netns exec if_bridge ip link set eth2 up
ip netns exec if_bridge ip link set br0  up

# Built in Ether
ip link set eth0 netns if_lan
ip netns exec if_lan ifconfig eth0 192.168.7.240
ip netns exec if_lan route add default gw 192.168.7.1


# Built in WiFi
iw phy phy0 set netns name if_2GHz
ip netns exec if_2GHz ifconfig wbin0 192.168.7.242
sleep 1
ip netns exec if_2GHz wpa_supplicant -B -c /etc/if_2GHz/wpa_supplicant/wpa_supplicant.conf -i wbin0

# USB attached WiFi
# As of 4/4/2020, the USB adapters I have do not support netns
#iw phy phy1 set netns name if_4GHz
# Also, there needs to be some interface in root namespace if you wish to logon.
ifconfig wusb0  192.168.7.245

# Now, start the daemons in the various namespaces
sleep 5
/home/pi/MonitorHomeISP/queueRecvDB.py >/tmp/queuRecvDB.log 2>&1 &
iperf3 -s -D -B 192.168.7.245 -J --logfile /tmp/iperfServer245.log 
ip netns exec if_2GHz iperf3 -s -D -B 192.168.7.242 --logfile /tmp/iperfServer242.log
ip netns exec if_lan /home/pi/MonitorHomeISP/testExec.py >/tmp/testExec.log 2>&1 &
ip netns exec if_bridge /home/pi/MonitorHomeISP/intfStats.py >/tmp/intfStats.log 2>&1 &

