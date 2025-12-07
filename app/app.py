from flask import (
    Blueprint,
    render_template,
    request,
    Response,
    stream_with_context,
)
import mlflow
import dspy
from crec.config import config
from crec.agent import Agent

bp = Blueprint("app", __file__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_query = data.get("message")

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("Testing")
    mlflow.dspy.autolog()

    lm = dspy.LM(
        model="ollama_chat/" + config.llm,
        api_base=config.llm_url,
        api_key=config.llm_api_key,
        max_tokens=config.context_window,
        temperature=config.llm_temperature,
    )
    dspy.configure(lm=lm)

    agent = Agent(
        max_iterations=5,
        streaming=True,
    )

    def generate():
        responses_gen = agent(user_query=user_query)
        for chunk in responses_gen:
            yield chunk  # Send piece by piece to client

    return Response(stream_with_context(generate()), mimetype="text/plain")
