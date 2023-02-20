from flask import Flask, request
import app_config
import requests, random, string, os
from datetime import datetime
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import msal

app = Flask(__name__)
app.config.from_object(app_config)
app.config["DEBUG"] = True

authority = "https://login.microsoftonline.com/b258091b-e0c8-406d-ab95-61fae999beee"
app_id = "88445fba-93f5-4848-b8a0-474058784036"
scope = ["https://graph.microsoft.com/.default"]


# Authenticate with Azure. First, obtain the DefaultAzureCredential
credential = DefaultAzureCredential()

# Next, get the client for the Key Vault. You must have first enabled managed identity
# on the App Service for the credential to authenticate with Key Vault.
key_vault_url = "https://jndemovault.vault.azure.net/"
keyvault_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Obtain the secret: for this step to work you must add the app's service principal to
# the key vault's access policies for secret management.
api_secret_name = "jndemo"
vault_secret = keyvault_client.get_secret(api_secret_name)

# The "secret" from Key Vault is an object with multiple properties. The key we
# want for the third-party API is in the value property. 
app_secret = vault_secret.value

jndemoApp = msal.ConfidentialClientApplication(
    app_id, authority=authority,
    client_credential=app_secret
)

result = jndemoApp.acquire_token_for_client(scopes=scope)
access_token = result["access_token"]

def check_role():
    try: 
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json"
        }

        response = requests.get(
            "https://graph.microsoft.com/v1.0/me/memberOf",
            headers=headers
        )

        if response.status_code == 200:
            roles = response.json().get("value", [])
            return str(roles)
        else:
            "Failed to get roles"
    except Exception as err:
        return str(err)


@app.route("/home")
def home():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return ('Authorization header is missing')
    token = auth_header.split(' ')[1]
    try:
        result = jndemoApp.acquire_token_on_behalf_of(
            token,
            scopes=['https://graph.microsoft.com/.default']
        )
        roles = result['id_token_claims']['roles']
        return str(roles)
    except Exception as e:
        return ('Authentication failed')
    #return " ******* "

if __name__ == "__main__":
    app.run()




'''# Protected route that requires "Admin" role
@app.before_request
def check_role():
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/memberOf",
        headers=headers
    )

    if response.status_code == 200:
        roles = response.json().get("value", [])
        # Check if the client has a specific role
        if "role_name" not in roles:
            return "Unauthorized", 401
    else:
        return "Failed to get roles", 500
@app.route("/protected_endpoint")
def protected_endpoint():
    # This endpoint is protected by the role check
    return "Hello, world!"

'''




'''By using Flask's before_request decorator and RBAC, you can ensure that your Flask web API is secure and that only clients with the appropriate roles can access protected endpoints.'''