import re,time
from httpAction import httpFunc, networkCreate

baseUrl = "http://172.16.7.45"
tokenGen = httpFunc(baseUrl)
tenantName = "admin"
username = "admin"
password = "password"

payload= {"auth": {"tenantName": tenantName, "passwordCredentials": {"username": username, "password": password}}}
token = tokenGen.createToken(payload)
print token


## Network Creation
#==================
netCreate = networkCreate(baseUrl, token)

#External Network

print "External Network and Subnet IDs"

extNetworkId = netCreate.createNetwork("ext-net", shared='true', external='true')
print extNetworkId
extSubnetId=netCreate.createSubnet(extNetworkId ,'172.16.7.0/24', allocation_pools=[{'start':'172.16.7.201','end':'172.16.7.209'}], gateway_ip="172.16.7.254", enable_dhcp='false', name='ext-subnet', dns_nameservers=["172.16.10.1","8.8.8.8"])
print extSubnetId

