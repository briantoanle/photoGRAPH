from flask import Flask, request, jsonify

from routes.projects import project_routes
from routes.users import user_routes
from flask_session import Session
import os
from flask_cors import CORS
app = Flask(__name__)

app.register_blueprint(user_routes, url_prefix="/api/users")
app.register_blueprint(project_routes, url_prefix="/api/projects")

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True  # Adds extra security
app.secret_key = os.getenv("SESSION_SECRET_KEY", "supersecretkey")

# Initialize Flask-Session
Session(app)
CORS(app)

@app.get("/")
def home():

    return "API successfully started"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use Railway's provided PORT
    app.run(host="0.0.0.0", port=port)
