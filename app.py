from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import app_config

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

@app.route("/home")
def home():
    if not "roles" in session["user"]:
        return "NO ROLE FOUND"
    roles = ""
    user_roles = session["user"]["roles"]
    for user_role in user_roles:
        roles = roles + "|" + user_role
    return "----- " + roles

if __name__ == "__main__":
    app.run()