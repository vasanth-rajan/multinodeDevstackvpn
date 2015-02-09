#!/usr/bin/env bash

source /home/stack/devstack/openrc admin admin

function associateFIPtoVm(){
    vmIp=$(nova list | grep $vmUuid | grep -Eo "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}")
    vmPortId=$(neutron port-list | grep $vmIp | awk -F "| " '{print $2}')
    fip=$(neutron floatingip-associate $fIPId $vmPortId)
}

vmUuid=$1
fIPId=$2
associateFIPtoVm
