Pre-requistes
#############

Create a user 'stack' in all the machines
Assign IP address as password  for created user 'stack'

Linux Command for creating a User in linux
==========================================
adduser stack 
echo "stack ALL=(ALL) NOPASSWD: ALL" » /etc/sudoers 
exit 

