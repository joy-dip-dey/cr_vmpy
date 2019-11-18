"""A deployer class to deploy a template on Azure"""
import os.path
import json
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode


class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.

    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """
    name_generator = Haikunator()

    def __init__(self, subscription_id, resource_group, pub_ssh_key_path='~/.ssh/id_rsa.pub', p_client, p_secret, p_tenant):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.dns_label_prefix = self.name_generator.haikunate()

        pub_ssh_key_path = os.path.expanduser(pub_ssh_key_path)
        # Will raise if file not exists or not enough permission

        with open(pub_ssh_key_path, 'r') as pub_ssh_file_fd:
             self.pub_ssh_key = pub_ssh_file_fd.read()

        print (self.pub_ssh_key)
        print('Press Enter SSH : ')

        self.credentials = ServicePrincipalCredentials(
            client_id = p_client,   #'fd8b4579-715d-4e07-a373-d490d57f6634',      #os.environ['AZURE_CLIENT_ID'],
            secret = p_secret,      #'V5p5M[:84DK/TUcD[d7mDlJKHkt=4TFL',         #os.environ['AZURE_CLIENT_SECRET'],
            tenant = p_tenant      #'e3cf3c98-a978-465f-8254-9d541eeea73c' #os.environ['AZURE_TENANT_ID']
        )
        self.client = ResourceManagementClient(self.credentials, self.subscription_id)

    def deploy(self):
        """Deploy the template to a resource group."""
        self.client.resource_groups.create_or_update(
            self.resource_group,
            {
                'location': 'westus'
            }
        )

        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'template.json')

        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)

        parameters = {
                      'sshKeyData': self.pub_ssh_key,
                      'vmName': 'azure-deployment-sample-vm',
                      'dnsLabelPrefix': self.dns_label_prefix
                     }
        parameters = {k: {'value': v} for k, v in parameters.items()}

        print (parameters.items())
        input('press enter : ') 
        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            'azure-sample',
            deployment_properties
        )
        deployment_async_operation.wait()

    def destroy(self):
        """Destroy the given resource group"""
        self.client.resource_groups.delete(self.resource_group)
