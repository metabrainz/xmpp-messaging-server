from __future__ import absolute_import
from flask import Blueprint, render_template
from webserver.xmpp.bosh_client import BOSHClient

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    bc = BOSHClient("test2@localhost", "test2", "http://localhost:5280/http-bind")
    bc.start_session_and_auth()
    return render_template("index.html", **dict(
            jid=bc.jid.full,
            sid=bc.sid,
            rid=bc.rid,
    ))
