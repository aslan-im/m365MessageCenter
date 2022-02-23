import os
import json
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential


class SecretsManager:
    __secrets = {}

    def __init__(self, secret):
        codeDir = os.path.dirname(os.path.abspath(__file__))
        self.__config_path = os.path.join(codeDir, 'configurations', 'config.json')
        self.__client_secret = secret
        self.__readConfigFile__()
        self.__readKeyVault__()

    def __readConfigFile__(self):
        with open(self.__config_path, 'r') as outfile:
            self.__json_string = json.load(outfile)
            
        self.__client_id = self.__json_string['secrets_manager']['client_id']
        self.__tenant_id = self.__json_string['secrets_manager']['tenant_id']
        self.__keyvault_name = self.__json_string['azure_keyvault']['keyvault_name']
        self.__tg_token_secret = self.__json_string['azure_keyvault']['tg_token_secret']
        self.__client_secret_secret = self.__json_string['azure_keyvault']['client_secret']
        self.__tg_errors_token_secret = self.__json_string['azure_keyvault']['tg_errors_token_secret']
        self.__secrets['time_delta'] = self.__json_string['main']['check_time_delta_minutes']
        self.__secrets['client_id'] = self.__json_string['graph']['client_id']
        self.__secrets['tenant_id'] = self.__json_string['graph']['tenant_id']
        self.__secrets['tg_prod_chat_id'] = self.__json_string['telegram']['prod_chat_id']
        self.__secrets['test_chat_id'] = self.__json_string['telegram']['test_chat_id']
        self.__secrets['errors_handler_chat_id'] = self.__json_string['telegram']['errors_handler_chat_id']
        self.__secrets['running_mode'] = self.__json_string['main']['mode']

    def __readKeyVault__(self):
        kv_uri = f"https://{self.__keyvault_name}.vault.azure.net"
        credential = ClientSecretCredential(self.__tenant_id, self.__client_id, self.__client_secret)
        client = SecretClient(kv_uri, credential)
        self.__secrets['client_secret'] = (client.get_secret(self.__client_secret_secret)).value
        self.__secrets['tg_token'] = (client.get_secret(self.__tg_token_secret)).value
        self.__secrets['tg_token_errors'] = (client.get_secret(self.__tg_errors_token_secret)).value

    def get_config(self):
        return self.__secrets