from __future__ import absolute_import
from flask import Blueprint, render_template, request, current_app, jsonify
from werkzeug.exceptions import BadRequest
from webserver.xmpp.bosh_session import BOSHSession

main_bp = Blueprint('main', __name__)


@main_bp.route("/connect")
def connect():
    username = request.args.get("username")
    if not username:
        raise BadRequest("You need to provide a username.")
    # TODO: Implement this properly
    jid = "%s@%s" % (username, current_app.config.get("XMPP_DOMAIN"))
    password = "hunter2"
    bs = BOSHSession(current_app.config.get("BOSH_ENDPOINT_INTERNAL"), jid, password)
    bs.start_session_and_auth()
    return jsonify({
        "jid": bs.jid.full,
        "sid": bs.sid,
        "rid": bs.rid,
    })


# TODO: Remove this view after testing is done:
@main_bp.route("/")
def index():
    return render_template("index.html")
