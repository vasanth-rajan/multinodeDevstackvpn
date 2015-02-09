#!/usr/bin/python
import os
import re

#computeHost=raw_input("Enter the Host IP:\n")
computeHost="172.16.7.211"
controllerIp = "172.16.7.45"

user="stack"
password="password"
fabFile="fabfile.py"

computeConf="compute_local.conf"

fi = open(computeConf,"r") 
content = fi.read()
fi.close()

lineNo = 0
contentLine = content.split("\n")
for line in contentLine:

    if (re.match("HOST_IP",line)):
        hostIp=line.split("=")
        occuredLine1 = lineNo

    if (re.match("SERVICE_HOST",line)):
        hostIp=line.split("=")
        occuredLine2 = lineNo

    lineNo= lineNo+1

contentLine[occuredLine1] = "HOST_IP=%s" %computeHost
contentLine[occuredLine2] = "SERVICE_HOST=%s" %controllerIp
newContent = "\n".join(contentLine)
#print newContent
os.rename(computeConf, ".tmp.conf")

fo = open(computeConf, "w")
fo.write(newContent)
fo.close()

os.system("fab -H %s -u %s -p %s -f %s gitPkg" %(computeHost, user, password, fabFile))
os.system("fab -H %s -u %s -p %s -f %s gitClone" %(computeHost, user, password, fabFile))
os.system("fab -H %s -u root -p %s -f %s copyLocal:user=%s,fileName=%s" %(computeHost, password, fabFile,user, computeConf))
os.system("fab -H %s -u %s -p %s -f %s devstackStart" %(computeHost, user, password, fabFile))
