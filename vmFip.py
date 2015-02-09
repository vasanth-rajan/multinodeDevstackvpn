import os,subprocess
import time 

from httpAction import httpFunc, vmCreate, routerCreate


def getEastNetId():
    cmd_1 = ['neutron', 'net-list']
    cmd_2 = ['awk', '/net_east/{print $2}']
    p1 = subprocess.Popen(cmd_1, stdout = subprocess.PIPE)
    p2 = subprocess.Popen(cmd_2, stdin = p1.stdout, stdout=subprocess.PIPE)
    id = p2.communicate()[0]
    return id

def getWestNetId():
    cmd_1 = ['neutron', 'net-list']
    cmd_2 = ['awk', '/net_west/{print $2}']
    p1 = subprocess.Popen(cmd_1, stdout = subprocess.PIPE)
    p2 = subprocess.Popen(cmd_2, stdin = p1.stdout, stdout=subprocess.PIPE)
    id = p2.communicate()[0]
    return id

def getExtNetId():
    cmd_1 = ['neutron', 'net-list']
    cmd_2 = ['awk', '/ext-net/{print $2}']
    p1 = subprocess.Popen(cmd_1, stdout = subprocess.PIPE)
    p2 = subprocess.Popen(cmd_2, stdin = p1.stdout, stdout=subprocess.PIPE)
    id = p2.communicate()[0]
    return id


if __name__ == '__main__':
     networkId1 = getEastNetId()
     print 'networkId1 = %s' %networkId1
     networkId2 = getWestNetId()
     print 'networkId2 = %s' %networkId2


baseUrl = "http://172.16.7.45"
tokenGen = httpFunc(baseUrl)
tenantName = "admin"
username = "admin"
password = "password"

payload= {"auth": {"tenantName": tenantName, "passwordCredentials": {"username": username, "password": password}}}
token = tokenGen.createToken(payload)
print token

novaVmInst = vmCreate(baseUrl, token)
vm1 = novaVmInst.createVmInstance("VPNaaSTestVm1", networkId1.rstrip())

vm2 = novaVmInst.createVmInstance("VPNaaSTestVm2", networkId2.rstrip())

time.sleep(30)

router = routerCreate(baseUrl, token)

extNetworkId=getExtNetId().rstrip() 
print "External Network UUID==", extNetworkId

floatingIp1 = router.createFloatingIp(extNetworkId)
floatingIp2 = router.createFloatingIp(extNetworkId)

os.system ("sudo bash floatingIp.sh %s %s" %(vm1, floatingIp1))
os.system ("sudo bash floatingIp.sh %s %s" %(vm2, floatingIp2))
