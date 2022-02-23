import requests

class GraphAPIRequests:

    def __init__(self, clientId, tenantId, clientSecret):
        self.client_id = clientId
        self.tenant_id = tenantId
        self.client_secret = clientSecret

    def get_token(self):
        uri = "https://login.microsoftonline.com/" + self.tenant_id + "/oauth2/v2.0/token"
        scope = "https://graph.microsoft.com/.default"
        post_request_body = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': scope
        }
        post_request = requests.post(uri, post_request_body)
        json_data = post_request.json()
        self.token = json_data

    def get_messages(self):
        token = self.token
        tenant = self.tenant_id
        authorization = token['token_type'] + " " + token['access_token']

        my_header = {
            'accept': 'application/json; odata.metadata=full',
            'Authorization': authorization
        }

        mc_resource = "admin/serviceAnnouncement/messages"
        uri = "https://graph.microsoft.com/v1.0/" + mc_resource
        request_result = []
        try:
            result_response = (requests.get(uri, headers=my_header)).json()
            request_result += result_response['value']            
            
        except BaseException as err:
            print(err)
            raise
        
        if '@odata.nextLink' in result_response:
            next_link_uri = result_response['@odata.nextLink']
        else:
            next_link_uri = None
        while(next_link_uri != None):
            try:
                result_response = (requests.get(next_link_uri, headers=my_header)).json()
                request_result += result_response['value']
                if '@odata.nextLink' in result_response:
                    next_link_uri = result_response['@odata.nextLink']
                else:
                    next_link_uri = None

            except BaseException as err:
                print(err)
                raise
                     
        
        if request_result:
            return request_result
        else:
            return None
         
