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

app = msal.ConfidentialClientApplication(
    app_id, authority=authority,
    client_credential=app_secret
)

result = app.acquire_token_for_client(scopes=scope)
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
    '''if not "roles" in session["user"]:
        return "NO ROLE FOUND"
    roles = ""
    user_roles = session["user"]["roles"]
    for user_role in user_roles:
        roles = roles + "|" + user_role
    return "----- " + roles'''
    return " ******* " + check_role()

if __name__ == "__main__":
    app.run()




'''# Protected route that requires "Admin" role
@app.route("/admin")
@bearer.token_required
@requires_role("Admin")
def admin():
    return {"message": "Welcome, Admin!"}

if __name__ == "__main__":
    app.run()
'''




'''In this example, we use the Flask-Bearer library to handle bearer token authentication, and we use the check_client_role function to check the client's role based on the roles included in the access token. We also define a requires_role decorator that can be used to protect routes that require a specific client role.

To use this app, you'll need to set the following configuration variables in a config.py file:


Replace {tenant_id} and {client_id} with your AAD tenant ID and client ID, respectively.

I hope this helps! Let me know if you have any questions.'''