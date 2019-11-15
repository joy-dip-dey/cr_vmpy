import os.path
from deployer import Deployer

class MyAction(Action):
    def run(self, p_tenant_id, p_client_id, p_client_secret, p_subs_id, p_resource_group):

        my_subscription_id = p_subs_id

# the resource group for deployment
        my_resource_group = p_resource_group

# the path to your rsa public key file
        my_pub_ssh_key_path = os.path.expanduser('~/.ssh/id_rsa.pub')

        msg = "\nInitializing the Deployer class with subscription id: {}, resource group: {}" \
              "\nand public key located at: {}...\n\n"
        msg = msg.format(my_subscription_id, my_resource_group, my_pub_ssh_key_path)
        print(msg)
        input('press enter : ')
# Initialize the deployer class
        deployer = Deployer(my_subscription_id, my_resource_group, my_pub_ssh_key_path)
        print("Beginning the deployment... \n\n")
# Deploy the template
        my_deployment = deployer.deploy()

        print("Done deploying!!\n\nYou can connect via: `ssh azureSample@{}.westus.cloudapp.azure.com`".format(deployer.dns_label_prefix))
        return(True)
# Destroy the resource group which contains the deployment
# deployer.destroy()
