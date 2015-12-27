from __future__ import absolute_import
from flask import Blueprint, render_template, request, current_app, jsonify
from werkzeug.exceptions import BadRequest
from webserver.xmpp.bosh_session import BOSHSession

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/connect")
def connect():
    jid = request.args.get("jid")
    password = request.args.get("password")
    if not (jid or password):
        raise BadRequest("You need to specify 'jid' and 'password' parameters.")
    bs = BOSHSession(current_app.config["BOSH_ENDPOINT_INTERNAL"], jid, password)
    bs.start_session_and_auth()
    return jsonify({
        "jid": bs.jid.full,
        "sid": bs.sid,
        "rid": bs.rid,
    })
