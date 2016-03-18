from neutron.api.rpc.agentnotifiers import l3_rpc_agent_api
from neutron.api.rpc.agentnotifiers import dhcp_rpc_agent_api
from neutron.api.rpc.handlers import dhcp_rpc
from neutron.api.rpc.handlers import metadata_rpc
from neutron.api.rpc.handlers import resources_rpc
from neutron.api.rpc.handlers import securitygroups_rpc
from oslo_config import cfg
from oslo_db import api as oslo_db_api
from oslo_db import exception as os_db_exception
from oslo_log import helpers as log_helpers
from oslo_serialization import jsonutils
from oslo_utils import excutils
from oslo_utils import importutils
from oslo_utils import uuidutils
from neutron.db import db_base_plugin_v2
from oslo_log import log as logging
from neutron.agent import securitygroups_rpc as sg_rpc
from neutron.db import securitygroups_rpc_base as sg_db_rpc
from neutron.db import extraroute_db
from neutron.db import agentschedulers_db
from neutron.db import address_scope_db
from neutron.db import agents_db
from neutron.db import agentschedulers_db
from neutron.db import allowedaddresspairs_db as addr_pair_db
from neutron.db import api as db_api
from neutron.db import db_base_plugin_v2
from neutron.db import dvr_mac_db
from neutron.db import external_net_db
from neutron.db import extradhcpopt_db
from neutron.db import models_v2
from neutron.db import netmtu_db
from neutron.api.v2 import attributes
from neutron.db.quota import driver  # noqa
from neutron.quota import resource_registry
from neutron.extensions import portbindings
from neutron import manager
from neutron.common import constants as const
from neutron.common import exceptions as exc
from neutron.common import ipv6_utils
from neutron.common import rpc as n_rpc
from neutron.common import topics
from neutron.common import utils
import os
from neutron.db import vlantransparent_db
from neutron.services.qos import qos_consts
import fcntl, socket, struct
from neutron.db import portbindings_base

LOG = logging.getLogger(__name__)


class MyNeutronPlugin(db_base_plugin_v2.NeutronDbPluginV2,
                      extraroute_db.ExtraRoute_db_mixin, sg_db_rpc.SecurityGroupServerRpcMixin, addr_pair_db.AllowedAddressPairsMixin,
                      external_net_db.External_net_db_mixin, netmtu_db.Netmtu_db_mixin, agentschedulers_db.AgentSchedulerDbMixin, vlantransparent_db.Vlantransparent_db_mixin,portbindings_base.PortBindingBaseMixin):

    def __init__(self):
        super(MyNeutronPlugin, self).__init__()
        self.base_binding_dict = self._get_base_binding_dict()
        portbindings_base.register_port_dict_function()
        self.supported_extension_aliases = [
            "provider", "external-net", "binding", "quotas", "security-group", "extraroute",
            "agent"]

    def create_network(self, context, network):
        with context.session.begin(subtransactions=True):
            net = super(MyNeutronPlugin, self).create_network(context, network)
            net_name = net['name']
            try:
                os.system("sudo ip netns add " + net_name)
            except Exception as e:
                raise Exception("Plugin raised exception, check logs")
        return net

    def update_network(self, context, id, network):
        with context.session.begin(subtransactions=True):
            net = super(
                MyNeutronPlugin,
                self).update_network(
                context,
                id,
                network)
            net_uuid = net['id']
            vlan_id = 'ns1'  # vlan id in number
            try:
                a = 1  # core functionality of network updation here
            except Exception as e:
                raise Exception("Plugin raised exception, check logs")
        return net

    def get_network(self, context, id, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            net = super(MyNeutronPlugin, self).get_network(context,
                                                           id, None)
        return self._fields(net, fields)

    def get_networks(self, context, filters=None, fields=None,
                     sorts=None, limit=None, marker=None, page_reverse=False):
        session = context.session
        with session.begin(subtransactions=True):
            nets = super(MyNeutronPlugin,
                         self).get_networks(context, filters, None, sorts,
                                            limit, marker, page_reverse)

        return [self._fields(net, fields) for net in nets]

    def delete_network(self, context, net_id):
        with context.session.begin(subtransactions=True):
            try:
                net = self.get_network(context, net_id)
                net_name = net['name']
                os.system("sudo ip netns delete " + net_name)
            except Exception as e:
                raise Exception("plugin raised exception, check logs")
            result = super(MyNeutronPlugin, self).delete_network(context,
                                                                 net_id)

        return result

    def create_port(self, context, port):
        with context.session.begin(subtransactions=True):
            neutron_port = super(MyNeutronPlugin, self).create_port(context, port)
            self._process_portbindings_create_and_update(context,
                                                         port['port'],
                                                         neutron_port)
            try:
                vethAend = neutron_port['name'] + '_endA'
                vethBend = vethAend + '_endB'
                os.system(
                    "sudo ip link add " +
                    vethAend +
                    " type veth peer name " +
                    vethBend)
                #net = self.get_subnet(context, port['fixed_ips']['subnet_id'])
                interface_mac=neutron_port['mac_address']
                os.system("sudo ifconfig "+vethAend+" hw ether "+ interface_mac)
                os.system("sudo ip link set " + vethAend + " up")
                #os.system("sudo ovs-vsctl add-port " + net['name'] + " " + vethBend)
               
            except Exception as e:
                raise Exception("Plugin raised exception, check logs"+interface_mac)
        return neutron_port

    def update_port(self, context, id, port):
        with context.session.begin(subtransactions=True):
            port = super(MyNeutronPlugin, self).update_port(context, id, port)
            try:
                a = 1  # core functionality of network creation here
            except Exception as e:
                raise Exception("Plugin raised exception, check logs")
        return port

    def get_port(self, context, id, fields=None):
        with context.session.begin(subtransactions=True):
            port = super(MyNeutronPlugin, self).get_port(context, id, None)
        return port

    def get_ports(self, context, filters=None, fields=None,
                  sorts=None, limit=None, marker=None,
                  page_reverse=False):
        with context.session.begin(subtransactions=True):
            port = super(
                MyNeutronPlugin, self).get_ports(context, filters, None,
                                                 sorts, limit, marker,
                                                 page_reverse)
        return port

    def delete_port(self, context, id):
        with context.session.begin(subtransactions=True):
            port = super(MyNeutronPlugin, self).delete_port(context, id, None)
            try:
                a = 1  # core functionality of network creation here
            except Exception as e:
                raise Exception("Plugin raised exception, check logs")
        return port

    def create_subnet(self, context, subnet):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(
                MyNeutronPlugin,
                self).create_subnet(
                context,
                subnet)
            try:
                name = result['name']
                ip = '10.10.10.3'
                os.system("sudo ovs-vsctl add-br " + name)
                net_uuid = result['network_id']
                net = self.get_network(context, net_uuid)
                network_name = net['name']
                vethAend = network_name + '_endA'
                vethBend = network_name + '_endB'
                os.system(
                    "sudo ip link add " +
                    vethAend +
                    " type veth peer name " +
                    vethBend)
                os.system(
                    "sudo ip link set " +
                    vethAend +
                    " netns " +
                    network_name)
                os.system("sudo ovs-vsctl add-port " + name + " " + vethBend)
                os.system(
                    "sudo ip netns exec " +
                    name +
                    " ifconfig " +
                    vethAend +
                    " " +
                    ip +
                    " up")
                os.system("sudo ip link set " + vethBend + " up")
            except Exception as e:
                raise Exception("Plugin raised exception, check logs")
        return result

    def update_subnet(self, context, id, subnet):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(
                MyNeutronPlugin,
                self).update_subnet(
                context,
                id,
                subnet)
            try:
                a = 1  # core functionality of network updation here
            except Exception as e:
                raise Exception("Plugin raised exception, check logs")
        return result

    def get_subnet(self, context, id, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(MyNeutronPlugin, self).get_subnet(context, id, None)
        return result

    def get_subnets(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None,
                    page_reverse=False):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(
                MyNeutronPlugin, self).get_subnets(context, filters, None,
                                                   sorts, limit, marker, page_reverse)
        return result

    def delete_subnet(self, context, id):
        session = context.session
        with session.begin(subtransactions=True):
            try:
                subnet = self.get_subnet(context, id)
                subnet_name = subnet['name']
                os.system("sudo ovs-vsctl --if-exists del-br " + subnet_name)
            except Exception as e:
                raise Exception("Plugin raised exception, check logs")
            result = super(MyNeutronPlugin, self).delete_subnet(context, id)
        return result
        
    def _get_base_binding_dict(self):
        binding = {
            portbindings.VIF_TYPE: portbindings.VIF_TYPE_BRIDGE,
            portbindings.VIF_DETAILS: {
                # TODO(rkukura): Replace with new VIF security details
                portbindings.CAP_PORT_FILTER:
                'security-group' in self.supported_extension_aliases}}
        return binding
