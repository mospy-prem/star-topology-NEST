from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.topology.topo_helper import topo_helper

#Todo
#for handling all types of runtime error 
class Error(Exception):
    def __init__(self,message):
        self.message=message
        #print(self.message)
#star_topology class

class star(topo_helper):
   
   #intialising only switch in topology
   s = Switch("s")
   def __init__(self,node_count,network_add): #constructor takes no of nodes and network id as parameter 
       self.node_count = node_count
       self.network_add = network_add
       self.network_creation()
       self.node_interface_list, self.node_list = self.topology_creation()
       self.assign_add()
       #print(self.node_list)
       #self.assign_add()
       # self.interface_address(self,h)
       #print(self.node_count,self.network_add)
       #eth = self.node_interface_list[3]
       #print(eth)
       #self.node_list[2].ping(eth.address)
   
   #creating a network for the topology 
   def network_creation(self):
       self.n = Network(self.network_add)   
       #return self.n
       
   #creating total nodes in a topology with respective name of each node eg: h1 for 1st node ....    
   def node_creation(self):
       node_list=[]
       for i in range(self.node_count):
           x=Node('h'+str(i+1))
           node_list.append(x)
           #print(node_list[i]) 
       return node_list    
   
   #assigning addresses for each interfaces on respective network only
   def assign_add(self):
       AddressHelper.assign_addresses(self.n)
       #node_list = self.node_creation()        
   
   #topology creation
   #connecting each interface of nodes with inteface of switch   
   def topology_creation(self):
       node_list = self.node_creation()
       node_interface_list = []
       switch_interface_list = []
       #with self.n:
       for i in range(self.node_count):
           (x,y) = connect(node_list[i], self.s, network=self.n)
           x.set_attributes("5mbit", "5ms")
           y.set_attributes("10mbit", "100ms")
           #print(x,",")
           node_interface_list.append(x)
           switch_interface_list.append(y)
       #print(node_interface_list,node_list)    
       return node_interface_list,node_list   
   
   #getting addresses of each interfaces and storing in the list 
   def interface_address(self,h):
       node_interface_add = []
       #node_list = self.node_creation()
       #ind = node_list[h]
       for i in self.node_interface_list:
           node_interface_add.append(i.address)
       return node_interface_add[h-1]
   
   #checking the working of star topology for all posiible pair of nodes
   def ping_all(self):
       #self.node_l = self.node_list
       for i in self.node_list:
           a=i._name
           for j in self.node_interface_list:
               s= str(j)
               b=s[11:]
               b=b.split('-')[0];
               if a != b:
                  print("=== PING from "+a+" to "+b+ " ===")
                  i.ping(j.address)
           print("\n")
   
   def get_node(self,n):
       return self.node_list[n-1]
   
   def get_eth(self,n):
       return self.node_interface_list[n-1]
   #checking connection between given two nodes 
   #def ping_one(self,n1 , n2):
       #print("=== PING from "+self.node_list[n1-1]._name +" to "+ self.node_list[n2-1]._name + " ===")
       #self.node_list[n1-1].ping(self.node_interface_list[n2-1].address)       
               
   #TOdo
   #assigning bandwith and delays for each interfaces in the topology            
           
                     
