# NeutronPlugin

Here in this repository I'm trying to write a plugin for OpenStack Neutron just like ML2, Neutron plugin is the core part of openstack networking, and provides all types of networking functions.

In order for a plugin to work we need to defing CRUD methods for basic components which in neutron are
PORT
SUBNET
NETWORK

This plugin can be configured from /etc/neutron/neutron.conf file by changing the 

#service_plugins = neutron.services.l3_router.l3_router_plugin.L3RouterPlugin
core_plugin = neutron.plugins.myplugin.neutron_plugin.MyNeutronPlugin

Neutron server can be restarted frm q-svc screen of screen -r. 




