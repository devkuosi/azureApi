from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import app_config
from flask import Flask, request
from functools import wraps
import requests
import jwt
import json

app = Flask(__name__)
app.config.from_object(app_config)
#app.config.from_object("config")
Session(app)

# Check client's role using AAD authentication
def check_client_role(client_role):
    # Get access token from request headers
    access_token = request.headers.get("Authorization").split(" ")[1]

    # Get AAD configuration
    aad_config_response = requests.get("https://login.microsoftonline.com/b258091b-e0c8-406d-ab95-61fae999beee/.well-known/openid-configuration")
    aad_config = json.loads(aad_config_response.text)

    # Verify access token
    jwt_header = jwt.get_unverified_header(access_token)
    if jwt_header["alg"] != "RS256":
        return False

    jwks_uri = aad_config["jwks_uri"]
    jwks_response = requests.get(jwks_uri)
    jwks = json.loads(jwks_response.text)

    kid = jwt_header["kid"]
    jwk = [key for key in jwks["keys"] if key["kid"] == kid][0]
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
    try:
        decoded_token = jwt.decode(
            access_token,
            public_key,
            algorithms=["RS256"],
            audience=app.config["88445fba-93f5-4848-b8a0-474058784036"],
        )
    except jwt.exceptions.InvalidTokenError:
        return False

    # Check client's role
    client_roles = decoded_token.get("roles", [])
    '''if client_role in client_roles:
        return True
    else:
        return False'''
    
    return str(client_roles)

# Decorator for checking client's role
def requires_role(client_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_client_role(client_role):
                return {"error": "Unauthorized"}, 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/home")
def home():
    '''if not "roles" in session["user"]:
        return "NO ROLE FOUND"
    roles = ""
    user_roles = session["user"]["roles"]
    for user_role in user_roles:
        roles = roles + "|" + user_role
    return "----- " + roles'''
    print(check_client_role(""))
    return " ########### "

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