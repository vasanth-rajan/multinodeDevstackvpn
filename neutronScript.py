#!/usr/bin/python
import os
import re

#neutronHost=raw_input("Enter the Host IP:\n")
neutronHost="172.16.7.212"
controllerIp = "172.16.7.45"

user="stack"
password="password"
fabFile="fabfile.py"

neutronConf="neutron_local.conf"

fi = open(neutronConf,"r") 
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

contentLine[occuredLine1] = "HOST_IP=%s" %neutronHost
contentLine[occuredLine2] = "SERVICE_HOST=%s" %controllerIp
newContent = "\n".join(contentLine)

os.rename(neutronConf, "tmp.conf")
fo = open(neutronConf, "w")
fo.write(newContent)
fo.close()

os.system("fab -H %s -u %s -p %s -f %s gitPkg" %(neutronHost, user, password, fabFile))
os.system("fab -H %s -u %s -p %s -f %s gitClone" %(neutronHost, user, password, fabFile))
os.system("fab -H %s -u root -p %s -f %s copyLocal:user=%s,fileName=%s" %(neutronHost, password, fabFile,user, neutronConf))
os.system("fab -H %s -u %s -p %s -f %s devstackStart" %(neutronHost, user, password, fabFile))

