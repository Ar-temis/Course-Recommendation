from flask import Flask

from .app import bp as app_bp
import socket
import threading
import subprocess


def start_mlflow_server():
    cmd = [
        "mlflow",
        "server",
        "--backend-store-uri",
        "sqlite:///dbs/mydb.sqlite",
        "--default-artifact-root",
        "./mlruns",
        "--host",
        "0.0.0.0",
        "--port",
        "5000",
    ]

    # Start MLflow server as a background process
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    print("MLflow server launched with PID:", process.pid)

    # Optional: stream MLflow logs
    for line in process.stdout:
        print("[MLFLOW]", line, end="")


def mlflow_running(port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return s.connect_ex(("127.0.0.1", port)) == 0


def create_app():
    if not mlflow_running():
        thread = threading.Thread(target=start_mlflow_server, daemon=True)
        thread.start()

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/",
    )

    app.register_blueprint(app_bp)

    return app
