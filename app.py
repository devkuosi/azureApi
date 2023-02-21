from flask import Flask
from flask_azure_oauth import FlaskAzureOauth

app = Flask(__name__)

app.config['AZURE_OAUTH_TENANCY'] = 'b258091b-e0c8-406d-ab95-61fae999beee'
app.config['AZURE_OAUTH_APPLICATION_ID'] = '88445fba-93f5-4848-b8a0-474058784036'

auth = FlaskAzureOauth()
auth.init_app(app)

# Define a protected route using the require_auth decorator
@app.route('/home')
@auth("testScope")
def protected_route():
    return 'This route is protected!'

if __name__ == '__main__':
    app.run()