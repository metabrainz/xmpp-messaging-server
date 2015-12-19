from __future__ import absolute_import
from flask import Blueprint

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    return "This works!"
