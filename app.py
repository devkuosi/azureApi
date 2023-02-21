from flask import Flask
from flask_azure_oauth import FlaskAzureOauth

app = Flask(__name__)


# Initialize the FlaskAzureOauth extension
oauth = FlaskAzureOauth(app)

# Define a protected route using the require_auth decorator
@app.route('/home')
@oauth.require_auth(allowed_audiences=['api://7953fd80-3dc9-4b19-8691-ff4a4cec0301'])
def protected_route():
    return 'This route is protected!'

if __name__ == '__main__':
    app.run()