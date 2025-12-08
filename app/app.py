from flask import (
    Blueprint,
    render_template,
    request,
    Response,
    stream_with_context,
)
from flask import current_app as app

bp = Blueprint("app", __file__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_query = data.get("message")

    def generate():
        responses_gen = app.agent(user_query=user_query)
        for chunk in responses_gen:
            yield chunk  # Send piece by piece to client

    return Response(stream_with_context(generate()), mimetype="text/plain")
