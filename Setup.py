import os
topology_file = open('matrix.txt','r')  # opening file
topology_line = topology_file.readline().strip().split()

fip = os.popen('ifconfig eth1 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1') #to retrieve IP address of reserved VCL host
HOST_IP=fip.read().strip()
bg_file = open('background.sh', 'w')
bg_file.close()
bg_file = open('background.sh','a')  #opening file in append mode
bg_file.write("#!/bin/bash"+"\n"+"#To Allow wireshark to access internal ports of hosts by adding iptable rules"+"\n"+"while true; do"+"\n"+"sudo iptables -P INPUT ACCEPT"+"\n"+"sudo iptables -P FORWARD ACCEPT"+"\n"+"sudo iptables -P OUTPUT ACCEPT"+"\n"+"sudo iptables -t nat -F"+"\n"+"sudo iptables -t mangle -F"+"\n"+"sudo iptables -F"+"\n"+"sudo iptables -X"+"\n"+"sudo iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE"+"\n")
#bg_file.write("\n")
for i in topology_line:
#To get docker IP using this command
    dip = os.popen("docker inspect -f \'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' "+i)
    DOCKER_IP = dip.read().strip()
#To format port IP of the individual container as per last 3 octects of IP(1702 for 172.17.0.2)
    portip = os.popen("docker inspect -f \'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' "+i+"| cut -d \".\" -f 2-4 | awk -F. \'{print $1\"\"$2\"\"$3}\'")
    PORT_NO = portip.read().strip()
#appending lines to background.sh file
    line1 = "sudo iptables -t nat -A PREROUTING -d {} -p tcp --dport {} -j DNAT --to {}:22".format(HOST_IP, PORT_NO, DOCKER_IP)
    bg_file.write(line1+"\n")
bg_file.write("done")

#To access host details host file in etc directory
host_file = open('/etc/hosts','a')
for i in topology_line:
    dip = os.popen("docker inspect -f \'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' " + i)
    DOCKER_IP = dip.read().strip()

    line3 = "{} {}".format(DOCKER_IP, i)
    host_file.write(line3 + "\n")
host_file.close()

result_file = open('connection.txt','w')
result_file.write("\n"+"========================================= "+"\n")
result_file.write("Host      |           " + " IP                |"+"\n")
result_file.write("=========================================|"+"\n")

for i in topology_line:

    dip = os.popen("docker inspect -f \'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' " + i)

    DOCKER_IP = dip.read().strip()
    line3 = "{}       |        {}            |".format(i, DOCKER_IP)

    result_file.write(line3 + "\n")
    result_file.write("          |                              |" + "\n")
result_file.write("========================================= "+"\n")
result_file.write("\n"+"#Wireshark Connection Commands"+"\n")

result_file.write("Use below commands to perform wireshark captures at any interface, Replace ethx with your interface name"+"\n\n")
result_file.write("========================================================================================================"+"\n")
result_file.write("Host     |            " + "                     Wireshark Command                                            |"+"\n")
result_file.write("========================================================================================================|"+"\n")
#"ssh -X root@152.46.19.96 -p 1702 tcpdump -U -s0 -n -w - -i eth1 | wireshark -k -i -"

for i in topology_line:

    dip = os.popen("docker inspect -f \'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' " + i)

    DOCKER_IP = dip.read().strip()

    portip = os.popen("docker inspect -f \'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' " + i + "| cut -d \".\" -f 2-4 | awk -F. \'{print $1\"\"$2\"\"$3}\'")

    PORT_NO = portip.read().strip()

    line4 = '{}      |        "ssh -X root@{} -p {} tcpdump -U -s0 -n -w - -i ethx | wireshark -k -i -" '.format(i, HOST_IP, PORT_NO)

    result_file.write(line4 + "\n")
    result_file.write("         |                                                                                              |" + "\n")
result_file.write("======================================================================================================== "+"\n")
result_file.close()
