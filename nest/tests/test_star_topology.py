from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.topology.star_topo import *

#star class take two parameter first as no of nodes and second as network id.

temp = star(5,"10.0.1.0/24")

#ping_all function will ping among all host
temp.ping_all();    

#ping_one function used to ping from one host to interface of another host by their respective node number:
n1 = 1
n2 = 3
h = temp.get_node(n1)
eth = temp.get_eth(n2)
h.ping(eth.address)