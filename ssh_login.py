#!/usr/bin/python

import sys, re 
import pexpect
import time

if (len(sys.argv) !=2):
    print "Invalid Input Format:"
else:
    hostIp = sys.argv[1]

    ssh_newkey = 'Are you sure you want to continue connecting'

    p = pexpect.spawn("ssh root@%s" %hostIp)
    p.logfile = sys.stdout

    i=p.expect([ssh_newkey,'password:'])
    if i==0:
        p.sendline('yes')
        i=p.expect([ssh_newkey,'password:'])
    if i==1:
        p.sendline("password")

    time.sleep(10)
    p.expect ("Last login:")
    p.sendline("users")
    time.sleep(10)
    p.expect ("root@")
    
    userList = p.before

    print "Users are", userList
    print "=================="

    if (re.search("stack", userList)):
        print "User stack exists"
    else:
        print "Create a new user stack"

    p.sendline("logout")
    p.expect ("Connection to %s closed." %hostIp)





#print a 
