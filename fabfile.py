from fabric.api import *


def host_type():
    run('uname -r')

def gitPkg():
    run('sudo apt-get install git -y')

def gitClone():
    run('git clone -b stable/icehouse https://github.com/openstack-dev/devstack.git')

def copyLocal(user, fileName):
    put(fileName,'/home/stack/devstack/local.conf')
    run('sudo chown %s:%s /home/stack/devstack/local.conf' %(user,user))

def devstackStart():
    run('./devstack/stack.sh')

