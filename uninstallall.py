#!/usr/bin/python
import os
import re

user="stack"
password="password"
fabFile="fabfile.py"

computeHost="172.16.7.211"
neutronHost="172.16.7.212"
controllerHost="172.16.7.45"

os.system("fab -H %s -u %s -p %s -f %s devstackEnd" %(computeHost, user, password, fabFile))
os.system("fab -H %s -u %s -p %s -f %s devstackEnd" %(neutronHost, user, password, fabFile))
os.system("fab -H %s -u %s -p %s -f %s devstackEnd" %(controllerHost, user, password, fabFile))

