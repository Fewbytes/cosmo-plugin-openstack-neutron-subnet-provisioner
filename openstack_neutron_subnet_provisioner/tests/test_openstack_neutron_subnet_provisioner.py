# vim: ts=4 sw=4 et
import json
import logging
import random
import string
import unittest

import openstack_neutron_network_provisioner.tasks as network_tasks
import openstack_neutron_subnet_provisioner.tasks as tasks

RANDOM_LEN = 3  # cosmo_test_neutron_XXX_something

class OpenstackSubnetProvisionerTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("test_openstack_host_provisioner")
        self.logger.level = logging.DEBUG
        self.logger.info("setUp called")
        self.neutron_client = tasks._init_client()
        self.name_prefix = 'cosmo_test_neutron_{0}_'.format(''.join(
            [random.choice(string.ascii_uppercase + string.digits) for i in range(RANDOM_LEN)]
        ))
        self.network_name = self.name_prefix + 'sub1'

    def tearDown(self):
        for net in self.neutron_client.list_networks()['networks']:
            if net['name'].startswith(self.name_prefix):
                self.neutron_client.delete_network(net['id'])

    def test_all(self):

        network = {'name': self.network_name}

        network_tasks.provision(network)
        network = network_tasks._get_network_by_name(self.neutron_client, self.network_name)
        self.assertIsNotNone(network)
        self.assertTrue(network['admin_state_up'])

        name = self.name_prefix + 'sub1'
        subnet = {
            'name': name,
            'cidr': '10.0.0.0/28',
            'ip_version': 4,
        }

        sn = tasks.provision(network_name=self.network_name, subnet=subnet)
        sn = tasks._get_subnet_by_name(self.neutron_client, name)
        self.assertIsNotNone(sn)

        tasks.terminate(subnet)
        sn = tasks._get_subnet_by_name(self.neutron_client, name)
        self.assertIsNone(sn)

if __name__ == '__main__':
    unittest.main()
