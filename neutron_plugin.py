from neutron.db import db_base_plugin_v2
from oslo_log import log as logging
import os
LOG = logging.getLogger(__name__)
class MyNeutronPlugin(db_base_plugin_v2.NeutronDbPluginV2):
        def __init__(self):
        	super(MyNeutronPlugin, self).__init__()
        	self.supported_extension_aliases = ["binding", "security-group","extraroute",
                                            "agent"]
        def create_network(self, context, network):
		    with context.session.begin(subtransactions=True):
		        net = super(MyNeutronPlugin, self).create_network(context, network)
		        net_name = net['name']
		        try:
		            os.system("sudo ip netns add "+net_name)
		        except Exception as e:
		            raise Exception("Plugin raised exception, check logs")
		    return net

        def update_network(self, context, id, network):
		    with context.session.begin(subtransactions=True):
		        net = super(MyNeutronPlugin, self).update_network(context, id, network)
		        net_uuid = net['id']
		        vlan_id = 'ns1' #vlan id in number
		        try:
		            a=1 #core functionality of network updation here
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
		            net=self.get_network(context,net_id)
		            net_name = net['name']
		            os.system("sudo ip netns delete "+net_name)
		        except Exception as e:
		            raise Exception("plugin raised exception, check logs")
		        result = super(MyNeutronPlugin, self).delete_network(context,
		                                                             net_id)

		    return result
            
        def create_port(self, context, port):
		    with context.session.begin(subtransactions=True):
		        port = super(MyNeutronPlugin, self).create_port(context, port)
		        try:
		            vethAend= port['name']
		            vethBend= vethAend + '_endB'
		            sub=get_subnet(contrxt,port['subnet_id'])
		            os.system("sudo ovs-vsctl add-port "+sub['name'] +" "+ vethBend)
		        except Exception as e:
		            raise Exception("Plugin raised exception, check logs")
		    return port

        def update_port(self, context, id, port):
		    with context.session.begin(subtransactions=True):
		        port = super(MyNeutronPlugin, self).update_port(context,id, port)
		        try:
		            a=1 #core functionality of network creation here
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
		        port = super(MyNeutronPlugin, self).get_ports(context, filters,None,
                  sorts, limit, marker,
                  page_reverse)
		    return port

        def delete_port(self, context, id):
		    with context.session.begin(subtransactions=True):
		        port = super(MyNeutronPlugin, self).delete_port(context, id, None)
		        try:
		            a=1 #core functionality of network creation here
		        except Exception as e:
		            raise Exception("Plugin raised exception, check logs")
		    return port
            
        def create_subnet(self, context, subnet):
		   session = context.session
		   with session.begin(subtransactions=True):
		       result = super(MyNeutronPlugin, self).create_subnet(context, subnet)
		       try:
		           name=result['name']
		           ip='10.10.10.3'
		           os.system("sudo ovs-vsctl add-br "+ name)
		           net_uuid=result['network_id']
		           net=self.get_network(context,net_uuid)
		           network_name=net['name']
		           vethAend= network_name + '_endA'
		           vethBend= network_name + '_endB'
		           os.system("sudo ip link add "+vethAend+" type veth peer name "+vethBend)
		           os.system("sudo ip link set "+vethAend+" netns "+network_name)
		           os.system("sudo ovs-vsctl add-port "+name+" "+ vethBend)
		           os.system("sudo ip netns exec "+name+" ifconfig "+vethAend+" "+ip+" up")
		           os.system("sudo ip link set "+vethBend+" up")
		       except Exception as e:
		           raise Exception("Plugin raised exception, check logs")		       
		   return result


        def update_subnet(self, context, id, subnet):
		   session = context.session
		   with session.begin(subtransactions=True):
		       result = super(MyNeutronPlugin, self).update_subnet(context, id, subnet)
		       try:
		           a=1 #core functionality of network updation here
		       except Exception as e:
		           raise Exception("Plugin raised exception, check logs")		       
		   return result

        def get_subnet(self, context, id, fields=None):
		   session = context.session
		   with session.begin(subtransactions=True):
		       result = super(MyNeutronPlugin, self).get_subnet(context, id,None)
		   return result

        def get_subnets(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None,
                    page_reverse=False):
		   session = context.session
		   with session.begin(subtransactions=True):
		       result = super(MyNeutronPlugin, self).get_subnets(context, filters,None,
                    sorts, limit, marker,page_reverse)
		   return result

        def delete_subnet(self, context, id):
		   session = context.session
		   with session.begin(subtransactions=True):
		       try:
		            subnet=self.get_subnet(context,id)
		            subnet_name = subnet['name']
		            os.system("sudo ovs-vsctl --if-exists del-br "+subnet_name)
		       except Exception as e:
		           raise Exception("Plugin raised exception, check logs")
		       result = super(MyNeutronPlugin, self).delete_subnet(context, id)		       
		   return result
