#!/usr/bin/python
import os
import re

#controllerHost=raw_input("Enter the Host IP:\n")
controllerHost="172.16.7.45"
controllerIp = "172.16.7.45"

user="stack"
password="password"
fabFile="fabfile.py"

controllerConf="controller_local.conf"

fi = open(controllerConf,"r") 
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

contentLine[occuredLine1] = "HOST_IP=%s" %controllerHost
contentLine[occuredLine2] = "SERVICE_HOST=%s" %controllerIp

newContent = "\n".join(contentLine)

os.rename(controllerConf, "tmp.conf")

fo = open(controllerConf, "w")
fo.write(newContent)
fo.close()


os.system("fab -H %s -u %s -p %s -f %s gitPkg" %(controllerHost, user, password, fabFile))
os.system("fab -H %s -u %s -p %s -f %s gitClone" %(controllerHost, user, password, fabFile))
os.system("fab -H %s -u root -p %s -f %s copyLocal:user=%s,fileName=%s" %(controllerHost, password, fabFile,user, controllerConf))
os.system("fab -H %s -u %s -p %s -f %s devstackStart" %(controllerHost, user, password, fabFile))

