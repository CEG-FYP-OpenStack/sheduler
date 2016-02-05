import random

from oslo_log import log as logging
from six.moves import range

import nova.conf
from nova import exception
from nova.i18n import _
from nova import rpc
from nova.scheduler import driver
from nova.scheduler import scheduler_options

CONF = nova.conf.CONF
LOG = logging.getLogger(__name__)

class DRFHScheduler(driver.Scheduler):
	"""Scheduler tha works based on drf"""
	def __init__(self,*args,**kwargs):
		super(DRFHScheduler,self).__init__(*args,** kwargs)
		self.options = scheduler_options.SchedulerOptions()
		self.notifier = rpc.get_notifier('scheduler')
	def select_destinations(self,context,spec_obj):
		"""This selects the hosts to run the instances"""
		self.notifier.info(
			context, 'scheduler.select_destinations.start',
			dict(request_spec=spec_obj.to_legacy_request_spec_dict()))
		num_instances = spec_obj.num_instances
		selected_hosts = self._scheduler(context, spec_obj)

		#Couldnt get enough hosts
		if len(selected_hosts) < num_instances:
			for host in selected_hosts:
				host.obj.updated = None

			LOG.debug('There are %(hosts)d hosts avilable but %(num_instances)d instances required to be built',{'hosts': len(selected_hosts), 'num_instances': num_instances })

			reason = _('There are not enough hosts available')
			raise exception.NoValidHost(reason=reason)

		dests = [dict(host=host.obj.host, nodename=host.obj.nodename,
				limits=host.obj.limits) for host in selected_hosts]

		self.notifier.info(
			context, 'scheduler.select_destination.end',
			dict(request_spec=spec_obj.to_legacy_request_spec_dict()))
		return dests
	def _get_configuration_options(self):
		"""Get options dict"""
		return self.options.get_configuration()
	
	def _scheduler(self, context, spec_obj):
		"""Return nodes that fulfill speifications"""
		elevated = context.elevated()
		config_options = self._get_configuration_options()

		hosts = self._get_all_host_states(elevated)

		selected_hosts = []
		num_instances = spec_obj.num_instances

		spec_obj.config_options = config_options
		for num in range(num_instances):
			hosts = self.host_manager.get_filtered_hosts(hosts, spec_obj, index=num) 
			if not hosts:
				break

			weighed_hosts = self.host_manager.get_weighed_hosts(hosts, spec_obj)

			scheduler_host_subset_size = max(1, CONF.scheduler_host_subset_size)
			if scheduler_host_subset_size < len(weighed_hosts):
                		weighed_hosts = weighed_hosts[0:scheduler_host_subset_size]		

			chosen_host = random.choice(weighed_hosts)
			LOG.debug("hosts selected by drfh %(hosts)s", {'hosts': hosts}) 
			LOG.debug("Saleem's Selected host: %(host)s", {'host': chosen_host})
			selected_hosts.append(chosen_host)
			chosen_host.obj.consume_from_request(spec_obj)
            		if spec_obj.instance_group is not None:
                		spec_obj.instance_group.hosts.append(chosen_host.obj.host)
                		spec_obj.instance_group.obj_reset_changes(['hosts'])
        	return selected_hosts

	def _get_all_host_states(self, context):
		return self.host_manager.get_all_host_states(context)
