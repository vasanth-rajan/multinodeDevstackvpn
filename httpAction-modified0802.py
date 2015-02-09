import requests
import json
import urlparse
import time
import random 
import subprocess
import shlex

###################################################
# HTTP & Keystone Definitions
###################################################

class httpFunc(object):

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl

    def httpGet(self, urlGet, urlHeader):
#        self.urlHttpGet = urlparse.urljoin(self.baseUrl, urlGet)
        self.response = requests.get (urlGet, headers= urlHeader)
        print self.response.text, self.response.status_code 
        if ( self.response.status_code == 200 or self.response.status_code == 300):
            self.outputGet = json.loads (self.response.text)
            return self.outputGet
        else:
            return 0

    def httpPost(self, urlPost, payload, urlHeader= {'content-type': 'application/json'}):
        self.response = requests.post (urlPost, data=json.dumps(payload), headers= urlHeader)
        print self.response.text, self.response.status_code 
        if ( self.response.status_code == 200 or self.response.status_code == 201 or self.response.status_code == 202):
            self.outputPost = json.loads (self.response.text)
            return self.outputPost
        else:
            return 0

    def httpPut(self, urlPut, payload, urlHeader= {'content-type': 'application/json'}):
#        self.urlHttpPut = urlparse.urljoin(self.baseUrl, urlPut)
        self.response = requests.put (urlPut, data=json.dumps(payload), headers= urlHeader)
        print self.response.status_code, self.response.text
        if ( self.response.status_code == 200 or self.response.status_code == 300):
            self.outputPut = json.loads (self.response.text)
            return self.outputPut
        else:
            return 0

    def httpDelete(self, urlDelete, urlHeader):
        self.urlHttpDelete = urlparse.urljoin(self.baseUrl, urlDelete)
        self.deleteResp = requests.delete(self.urlHttpDelete, headers=urlHeader)
        if ( self.deleteResp.status_code == 204 or self.deleteResp.status_code == 200 or self.deleteResp.status_code == 300):
            return 1
        else:
            return 0

    def createToken(self, payload):

        self.urlHttpPost = urlparse.urljoin(self.baseUrl+':35357', 'v2.0/tokens?name=admin')
        self.urlHeaders = {'content-type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'python-keystoneclient'} 

        self.postResp = self.httpPost(self.urlHttpPost, payload, self.urlHeaders)
        if (self.postResp != 0):
#            self.tokenOp = self.postResp[u'access'][u'token']
            self.tokenOp = self.postResp[u'access'][u'token'][u'id']
            return self.tokenOp
        else:
            return 0

    def identifyTenant(self, token, tenantName='admin'):

        self.urlHttpGet = urlparse.urljoin(self.baseUrl+':35357', 'v2.0/tenants?name=%s' %tenantName)
        self.urlHeaders = {'content-type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'python-keystoneclient','X-Auth-Token': token}

        self.postResp = self.httpGet(self.urlHttpGet, self.urlHeaders)
        if (self.postResp != 0):
            self.tenantId = self.postResp[u'tenant'][u'id']
            return self.tenantId
        else:
            return 0



###################################################
# Neutron Network Creation Definitions
###################################################

class networkCreate(httpFunc):

    def __init__(self, baseUrl, token):
        super(networkCreate, self).__init__(baseUrl)
        self.neutronUrl = self.baseUrl+':9696'
        self.token = token
        self.urlHeaders = {'content-type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'python-neutronclient', 'X-Auth-Token': token}
 
    def createNetwork(self, networkName, **kwargs):
        if (kwargs.has_key('shared') == False):
            kwargs['shared'] = 'false'
        if (kwargs.has_key('external')== False):
            kwargs['external'] = 'false'
        
        self.urlHttpPost = urlparse.urljoin(self.neutronUrl, 'v2.0/networks.json')


        self.payload = {"network": {"shared": kwargs['shared'], "router:external": kwargs['external'], "name": networkName, "admin_state_up": "true"}}

        self.postResp = super(networkCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.networkId = self.postResp[u'network'][u'id']
            return self.networkId
        else:
            return 0

    def createSubnet(self, networkId, cidr, **kwargs):
        self.urlHttpPost = urlparse.urljoin(self.neutronUrl, 'v2.0/subnets.json')

        self.payload = { "subnet": {"ip_version": 4,"network_id": networkId, "cidr": cidr}}

        if (kwargs.has_key('allocation_pools') == True):
            self.payload['subnet']['allocation_pools'] = kwargs['allocation_pools']
        if (kwargs.has_key('gateway_ip')== True):
            self.payload['subnet']['gateway_ip'] = kwargs['gateway_ip']
        if (kwargs.has_key('name')== True):
            self.payload['subnet']['name'] = kwargs['name']
        if (kwargs.has_key('enable_dhcp')== True):
            self.payload['subnet']['enable_dhcp'] = kwargs['enable_dhcp']
        if (kwargs.has_key('dns_nameservers')== True):
            self.payload['subnet']['dns_nameservers'] = kwargs['dns_nameservers']

        self.postResp = super(networkCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.subnetId = self.postResp[u'subnet'][u'id']
            return self.subnetId
        else:
            return 0


###################################################
# Neutron Router Creation Definitions
###################################################

class routerCreate(httpFunc):

    def __init__(self, baseUrl, token):
        super(routerCreate, self).__init__(baseUrl)
        self.neutronUrl = self.baseUrl+":9696"
        self.token = token
        self.urlHeaders = {'content-type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'python-neutronclient', 'X-Auth-Token': self.token}

    def createRouter(self, routerName, **kwargs):
 
        self.payload = {"router": {"name": routerName, "admin_state_up": 'true'}}

        if (kwargs.has_key('network_id') == True):
            self.payload['router']['external_gateway_info'] = {}
            self.payload['router']['external_gateway_info']['network_id'] = kwargs['network_id']

        self.urlHttpPost = urlparse.urljoin(self.neutronUrl, 'v2.0/routers.json')

        self.postResp = super(routerCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.routerId = self.postResp[u'router'][u'id']
            return self.routerId
        else:
            return 0

    def routerAddInterface(self, routerId, interfaceId):
        self.urlHttpPut = urlparse.urljoin(self.neutronUrl, "v2.0/routers/%s/add_router_interface.json" %routerId)

        self.payload = {"subnet_id": interfaceId} 

        self.postResp = super(routerCreate, self).httpPut(self.urlHttpPut, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.portId = self.postResp[u'port_id']
            return self.portId
        else:
            return 0

    def createFloatingIp(self, extNetworkId):
        self.payload = {"floatingip": {"floating_network_id": extNetworkId }}

        self.urlHttpPost = urlparse.urljoin(self.neutronUrl, 'v2.0/floatingips.json')

        self.postResp = super(routerCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.floatingIpId = self.postResp[u'floatingip'][u'id']
            return self.floatingIpId
        else:
            return 0


    def vpnIkePolicyCreate(self):
        self.payload = {"ikepolicy": {"encryption_algorithm": "aes-128", "pfs": "group5", "phase1_negotiation_mode": "main", "name": "ikepolicy", "auth_algorithm": "sha1", "ike_version": "v1"}}

        self.urlHttpPost = urlparse.urljoin(self.neutronUrl, 'v2.0/vpn/ikepolicies.json')

        self.postResp = super(routerCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.ikePolicyId = self.postResp[u'ikepolicy'][u'id']
            return self.ikePolicyId
        else:
            return 0


    def vpnIpsecPolicyCreate(self):
        self.payload = {"ipsecpolicy": {"encapsulation_mode": "tunnel", "encryption_algorithm": "aes-128", "pfs": "group5", "name": "ipsecpolicy", "transform_protocol": "esp", "auth_algorithm": "sha1"}}

        self.urlHttpPost = urlparse.urljoin(self.neutronUrl, 'v2.0/vpn/ipsecpolicies.json')

        self.postResp = super(routerCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.ipsecPolicyId = self.postResp[u'ipsecpolicy'][u'id']
            return self.ipsecPolicyId
        else:
            return 0

    def vpnServiceCreate(self, vpnName, routerId, subnetId):

        self.urlHttpPost = urlparse.urljoin(self.neutronUrl, 'v2.0/vpn/vpnservices.json')

        self.payload = {"vpnservice": {"subnet_id": subnetId, "router_id": routerId, "description": "My vpn service", "name": vpnName, "admin_state_up": "true"}} 

        self.postResp = super(routerCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.vpnServiceId = self.postResp[u'vpnservice'][u'id']
            return self.vpnServiceId
        else:
            return 0


    def vpnIpsecSiteConnection(self, vpnConnName, peerIp, peerPvtCidr, vpnServiceId, ikePolicyId, ipsecPolicyId, pskKey='secret'):
        
        self.urlHttpPost = urlparse.urljoin(self.neutronUrl, 'v2.0/vpn/ipsec-site-connections.json')

        self.payload = {"ipsec_site_connection": {"psk": pskKey, "peer_cidrs": peerPvtCidr, "ikepolicy_id": ikePolicyId, "vpnservice_id": vpnServiceId, "peer_address": peerIp, "initiator": "bi-directional", "name": vpnConnName, "admin_state_up": "true", "mtu": "1500", "ipsecpolicy_id": ipsecPolicyId, "peer_id": peerIp}}

        self.postResp = super(routerCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.ipsecConnectId = self.postResp[u'ipsec_site_connection'][u'id']
            return self.ipsecConnectId
        else:
            return 0








###################################################
# Nova VM Creation Definitions
###################################################

class vmCreate(httpFunc):

    def __init__(self, baseUrl, token):
        super(vmCreate, self).__init__(baseUrl)
        self.novaUrl = self.baseUrl+":8774"
        self.token = token
        self.urlHeaders = {'content-type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'python-novaclient', 'X-Auth-Token': self.token}
        self.tenantId = super(vmCreate, self).identifyTenant(self.token, 'admin')



    def novaImageDetail(self):
 
        self.urlHttpGet = urlparse.urljoin(self.novaUrl, 'v2/%s/images/detail' %(self.tenantId))

        self.getResp = super(vmCreate, self).httpGet(self.urlHttpGet, self.urlHeaders)
        if (self.getResp != 0):
            self.imageId = self.getResp[u'images'][0][u'id']
            return self.imageId
        else:
            return 0

      
    def createVmInstance(self, vmName, networkId):
        self.imageId = self.novaImageDetail()

        self.payload = {"server": {"name": vmName, "imageRef": self.imageId, "flavorRef": "2", "max_count": 1, "min_count": 1, "networks": [{"uuid": networkId}]}}

        self.urlHttpPost = urlparse.urljoin(self.novaUrl, 'v2/%s/servers' %self.tenantId)

        self.postResp = super(vmCreate, self).httpPost(self.urlHttpPost, self.payload, self.urlHeaders)
        if (self.postResp != 0):
            self.vmId = self.postResp[u'server'][u'id']
            return self.vmId
        else:
            return 0

    def allVmInstanceDetails(self):
 
        self.urlHttpGet = urlparse.urljoin(self.novaUrl, 'v2/%s/servers/detail' %self.tenantId)

        self.postResp = super(vmCreate, self).httpGet(self.urlHttpGet, self.urlHeaders)
        if (self.postResp != 0):
            self.vmlist = []
            for vm in self.postResp[u'servers']:
                self.vmlist.append(vm[u'name'])
            return self.vmlist
        else:
            return 0


    def vmInstanceDetail(self, vmId):
 
        self.urlHttpGet = urlparse.urljoin(self.novaUrl, 'v2/%s/servers/%s' %(self.tenantId, vmId))

        self.postResp = super(vmCreate, self).httpGet(self.urlHttpGet, self.urlHeaders)
        if (self.postResp != 0):
            self.vmDetail = self.postResp[u'server']
            return self.vmDetail
        else:
            return 0






"""
    def accountStatus(self, token, acId):
        self.urlAccount = 'accounts/%s' %acId
        self.urlHeader = {'Authorization' : 'Bearer %s' %token}

        self.respGet = super(networkCreate, self).httpGet(self.urlAccount, self.urlHeader)
        if (self.respGet != 0):
            return self.respGet
        else:
            return 0

    def getAccountIdFromUsers(self, token, emailId):
        self.urlHeader = {'Authorization' : 'Bearer %s' %token}
        self.userNotFound = 0

        self.respGet = super(networkCreate, self).httpGet ('users', self.urlHeader)

        for self.user in self.respGet[u'users']:
            if (self.user[u'email'] == emailId):
                self.userNotFound=0
                return self.user[u'account'],self.user[u'id']
                break

            self.userNotFound = self.userNotFound + 1

        if (self.userNotFound == len(self.respGet[u'users'])):
            return 0


    def deleteAccount(self, token, acId):
        self.accountId = "accounts/%s" %(acId)
        self.urlHeader = {'Authorization' : 'Bearer %s' %token}

        self.deleteResp = super(networkCreate, self).httpDelete(self.accountId,self.urlHeader)
        if ( self.deleteResp == 1):
            return 1
        else:
            return 0

    
    def registerDevice(self, token, userId, osType=None):
        self.urlHeaders = {'content-type': 'application/json', 'Authorization' : 'Bearer %s' %token}
        self.mac = [ 0x00, 0xee, 0xff,
                random.randint(0x00, 0x7f),
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff) ]

        self.macAddr = ':'.join(map(lambda x: "%02x" % x, self.mac))
  
        if (osType == "Android"):
            self.deviceModel = "Sony Xperia Z"
            self.version = "4.4.4"
            self.deviceType = "Mobile"

        elif (osType == "iOS"):
            self.deviceModel = "IPhone 6S Plus"
            self.version = "8.0.1"
            self.deviceType = "Tablet"
       
        else:
            osType = "Windows"
            self.deviceModel = "Dell"
            self.version = "8.0"
            self.deviceType = "Desktop"

            

        self.payload = {
        "device": {
        "hwIdentifier": "%s" %(self.macAddr),
        "hwModel": "%s" %(self.deviceModel),
        "type": "%s" %(self.deviceType),
        "osName": "%s" %osType,
        "osVersion": "%s" %(self.version),
        "user": "%s" %userId
        }
        }


        self.postResp = super(networkCreate, self).httpPost('devices', self.payload, self.urlHeaders)
        if (self.postResp != 0):
            return 1
        else:
            return 0

"""



import re,time

baseUrl = "http://172.24.4.13"
tokenGen = httpFunc(baseUrl)
payload= {"auth": {"tenantName": "admin", "passwordCredentials": {"username": "admin", "password": "password"}}}
token = tokenGen.createToken(payload)
print token


## Network Creation
#==================
netCreate = networkCreate(baseUrl, token)

#External Network

print "External Network and Subnet IDs"

extNetworkId = netCreate.createNetwork("ext-net", shared='true', external='true')
print extNetworkId
extSubnetId=netCreate.createSubnet(extNetworkId ,'172.24.4.0/24', allocation_pools=[{'start':'172.24.4.201','end':'172.24.4.209'}], gateway_ip="172.24.4.254", enable_dhcp='false', name='ext-subnet', dns_nameservers=["172.24.10.1","8.8.8.8"])
print extSubnetId


#print "Private Network IDs"
# Private Network
#networkId1 = netCreate.createNetwork("admin-net1")
#print networkId1
#subnetId1 = netCreate.createSubnet(networkId1 ,'192.168.2.0/24', gateway_ip="192.168.2.1", name='admin-subnet1')
#print subnetId1


#networkId2 = netCreate.createNetwork("admin-net2")
#print networkId2
#subnetId2 = netCreate.createSubnet(networkId2 ,'192.168.1.0/24', gateway_ip="192.168.1.1", name='admin-subnet2')
#print subnetId2

## Router Creation
#=================
#print "Router and Port IDs"
#router_Create = routerCreate(baseUrl, token)
#routerId1 = router_Create.createRouter("admin-router1", network_id=extNetworkId)
#print routerId1
#portId1 = router_Create.routerAddInterface(routerId1, subnetId1)
#print portId1

#routerId2 = router_Create.createRouter("admin-router2", network_id=extNetworkId)
#print routerId2
#portId2 = router_Create.routerAddInterface(routerId2, subnetId2)
#print portId2

#VM Creation
#===========

#print "VM IDs"
#novaVmInst = vmCreate(baseUrl, token)


##run_command1 = "`neutron net-list -- --name $network --fields id | tail -n 2 | head -n 1 | cut -d' ' -f 2`"
#run_command1 = "`neutron net-list | awk '/net_east/{print $2}'`"
#args1 = shlex.split(run_command1)
#networkId1, errors = subprocess.Popen(args1, stdout = subprocess.PIPE, stderr= subprocess.PIPE, shell=True).communicate()

##Another way to get output
##output = subprocess.Popen(args,stdout = subprocess.PIPE).stdout

#print networkId1

#vm1 = novaVmInst.createVmInstance("VPNaaSTestVm1", networkId1)
#print vm1


#run_command2 = "`neutron net-list | awk '/net_west/{print $2}'`"
#args2 = shlex.split(run_command2)
#networkId2, errors = subprocess.Popen(args2, stdout = subprocess.PIPE, stderr= subprocess.PIPE, shell=True).communicate()

#print networkId2

print "VM IDs"
novaVmInst = vmCreate(baseUrl, token)

def EastNetIDInfo():
	networkId1 = getEastNetId()
	print 'networkId1 = %s' %networkId1
        return %networkId1

def getEastNetId():
	cmd_1 = ['neutron', 'net-list']
	cmd_2 = ['awk', '/net_east/{print $2}']
	p1 = subprocess.Popen(cmd_1, stdout = subprocess.PIPE)
	p2 = subprocess.Popen(cmd_2, stdin = p1.stdout, stdout=subprocess.PIPE)
	id = p2.communicate()[0]
	return id

def WestNetIDInfo():
	networkId1 = getWestNetId()
	print 'networkId2 = %s' %networkId2
        return %networkId2

def getWestNetId():
	cmd_1 = ['neutron', 'net-list']
	cmd_2 = ['awk', '/net_west/{print $2}']
	p1 = subprocess.Popen(cmd_1, stdout = subprocess.PIPE)
	p2 = subprocess.Popen(cmd_2, stdin = p1.stdout, stdout=subprocess.PIPE)
	id = p2.communicate()[0]
	return id


#if __name__ == '__main__':
#	EastNetIDInfo()
#       WestNetIDInfo()

vm1 = novaVmInst.createVmInstance("VPNaaSTestVm1", EastNetIDInfo())
print vm1

vm2 = novaVmInst.createVmInstance("VPNaaSTestVm2", WestNetIDInfo())
print vm2

time.sleep(10)

##VPN Connection Establishment
#=============================

#print "IKE Policy IDs"
#ikePolicyId = router_Create.vpnIkePolicyCreate()
#print ikePolicyId

#ipsecPolicyId = router_Create.vpnIpsecPolicyCreate()
#print ipsecPolicyId

#print "Service IDs"
#vpnServiceId1 = router_Create.vpnServiceCreate("vpnEastEnd", routerId1, subnetId1)
#print vpnServiceId1
#vpnServiceId2 = router_Create.vpnServiceCreate("vpnWestEnd", routerId2, subnetId2)
#print vpnServiceId2

#eastPeerIp = "172.24.4.202" 
#westPeerIp = "172.24.4.201"

##vpnConn1 = router_Create.vpnIpsecSiteConnection("EastEndIpsecConn", westPeerIp, "[192.168.32.0/24]", vpnServiceId1, ikePolicyId, ipsecPolicyId)
##vpnConn2 = router_Create.vpnIpsecSiteConnection("WestEndIpsecConn", eastPeerIp, "[192.168.31.0/24]", vpnServiceId2, ikePolicyId, ipsecPolicyId)

#vpnConn1 = router_Create.vpnIpsecSiteConnection("EastEndIpsecConn", westPeerIp, "172.24.4.0", vpnServiceId1, ikePolicyId, ipsecPolicyId)
#vpnConn2 = router_Create.vpnIpsecSiteConnection("WestEndIpsecConn", eastPeerIp, "172.24.4.0", vpnServiceId2, ikePolicyId, ipsecPolicyId)

#vpnConn1 = router_Create.vpnIpsecSiteConnection("EastEndIpsecConn", westPeerIp, "[192.168.32.1]", vpnServiceId1, ikePolicyId, ipsecPolicyId)
#vpnConn2 = router_Create.vpnIpsecSiteConnection("WestEndIpsecConn", eastPeerIp, "[192.168.31.1]", vpnServiceId2, ikePolicyId, ipsecPolicyId)

#print vpnConn1, vpnConn2
