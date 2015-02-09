#!/usr/bin/env bash

source /home/stack/devstack/openrc admin admin

WEST_SUBNET='192.168.31.0/24'
EAST_SUBNET='192.168.32.0/24'

function setup_site(){
    local site_name=$1
    local cidr=$2
    neutron net-create net_$site_name
    neutron subnet-create --name subnet_$site_name net_$site_name $2
}

function setup_router_and_vpn(){
    local site_name=$1
    EXT_NW_ID=`neutron net-list | awk '/ext-net/{print $2}'`
    neutron router-create router_$site_name
    neutron router-interface-add router_$site_name subnet_$site_name
    neutron router-gateway-set router_$site_name $EXT_NW_ID
    #neutron router-gateway-set router_$site_name `neutron net-list | awk '/{net_'$site_name'}/{print $2}'`
#    neutron vpn-service-create --name vpn_$site_name router_$site_name subnet_$site_name
}


function get_external_ip(){
    local router_id=`neutron router-show $1 | awk '/ id /{print $4}'`
    echo `neutron port-list -c fixed_ips -c device_id -c device_owner|grep router_gateway | awk '/'.$router_id.'/{print $5}' | sed 's/["}]//g'`
}

function clean_site(){
    local site_name=$1
    neutron ipsec-site-connection-delete ipsec_conn_$site_name    
    neutron vpn-service-list | awk '/vpn_'$site_name'/{print "neutron vpn-service-delete " $2}' | bash
    neutron router-gateway-clear router_$site_name
    neutron router-interface-delete router_$site_name subnet_$site_name
    neutron router-list | awk '/router_'$site_name'/{print "neutron router-delete " $2}' | bash
    neutron subnet-list | awk '/subnet_'$site_name'/{print "neutron subnet-delete " $2}' | bash
    neutron net-list | awk '/net_'$site_name'/{print "neutron net-delete " $2}' | bash
}

function setup(){
    neutron vpn-ikepolicy-create ikePolicyId
    neutron vpn-ipsecpolicy-create ipsecPolicyId
    setup_site west $WEST_SUBNET
    setup_site east $EAST_SUBNET
  
    ##Call httpaction.py here to enble ext-net creation
    python extNet.py

    setup_router_and_vpn west $WEST_SUBNET
    setup_router_and_vpn east $EAST_SUBNET

    WEST_IP=$(get_external_ip router_west)
   #setup_site east $EAST_SUBNET
    EAST_IP=$(get_external_ip router_east)

    python vmFip.py

#    vpnServiceId1=`neutron vpn-service-list -- --name vpn_east --fields id | tail -n 2 | head -n 1 | cut -d' ' -f 2`
#    vpnServiceId2=`neutron vpn-service-list -- --name vpn_west --fields id | tail -n 2 | head -n 1 | cut -d' ' -f 2`

#    neutron ipsec-site-connection-create --name ipsec_conn_east --vpnservice-id $vpnServiceId1 --ikepolicy-id ikePolicyId --ipsecpolicy-id ipsecPolicyId --peer-address $WEST_IP --peer-id $WEST_IP --peer-cidr $WEST_SUBNET --psk secrete 
#    neutron ipsec-site-connection-create --name ipsec_conn_west --vpnservice-id $vpnServiceId2 --ikepolicy-id ikePolicyId --ipsecpolicy-id ipsecPolicyId --peer-address $EAST_IP --peer-id $EAST_IP --peer-cidr $EAST_SUBNET --psk secrete
}

function cleanup(){
    clean_site west
    clean_site east
    neutron vpn-ikepolicy-delete ikePolicyId
    neutron vpn-ipsecpolicy-delete ipsecPolicyId
}

cleanup
setup
