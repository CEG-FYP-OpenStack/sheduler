import MySQLdb

class InstanceManager(object):
	"""docstring for InstanceManager"""
	node_details = []

	def __init__(self):
		super(InstanceManager, self).__init__()
		node_details = []

	def node_details(self):
		db = MySQLdb.connect("127.0.0.1","root","password","nova")
		cursor = db.cursor()
		cursor.execute("select free_disk_gb,free_ram_mb,vcpus,vcpus_used,uuid,local_gb,memory_mb,host,hostname from compute_nodes")

		data = cursor.fetchall()
		for row in data:
			node_details_dict = {}
			free_disk = row['free_disk_gb']
			free_ram = row['free_ram_mb']
			free_vcpus = row['vcpus'] - row['vcpus_used']
			total_disk = row['local_gb']
			total_ram = row['memory_mb']
			total_vcpus = row['vcpus']
			nodename = row['host']
			hostname = row['hostname']
			node_details_dict['nodename'] = nodename
			node_details_dict['free_disk'] = free_disk
			node_details_dict['free_ram'] = free_ram
			node_details_dict['free_vcpus'] = free_vcpus
			node_details_dict['total_disk'] = total_disk
			node_details_dict['total_ram'] = total_ram
			node_details_dict['total_vcpus'] = total_vcpus
			node_details_dict['hostname'] = hostname
			self.node_details.append(node_details_dict)

		return self.node_details

	def feasible_nodes(self, vm):
		nodes = []

		db = MySQLdb.connect("127.0.0.1","root","password","nova")
		cursor = db.cursor()
		query_string = 'select uuid,host from compute_nodes where free_ram_mb >= '+ str(vm['ram']) +' and vcpus-vcpus_used >= '+str(vm['vcpus'])+' and local_gb-local_gbused >= '+str(vm['disk'])+''
		cursor.execute(query_string)

		data = cursor.fetchall()

		for row in data:
			node_dict = {}
			hostname = row['hostname']
			uuid = row['uuid']
			node_dict['hostname'] = hostname
			node_dict['uuid'] = uuid
			nodes.append(node_dict)

		return nodes
	
	def vm_list(self,hostname):
		vm_list = []
		
		db = MySQLdb.connect("127.0.0.1","root","password","nova")
		cursor = db.cursor()
		query_string = 'select display_name,memory_mb,vcpus,root_gb from instances where host='+hostname+''
		cursor.execute(query_string)

		data = cursor.fetchall()

		for row in data:
			vm_data = {}
			display_name = row['display_name']
			ram = row['memory_mb']
			vcpus = row['vcpus']
			disk = row['root_gb']

			vm_data['ram'] = ram
			vm_data['vcpus'] = vcpus
			vm_data['disk'] = disk

			vm_list.append(vm_data)

		return vm_list