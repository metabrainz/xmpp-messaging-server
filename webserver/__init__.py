from flask import Flask
import sys
import os


def create_app():
    app = Flask(__name__)

    # Configuration
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
    import config
    app.config.from_object(config)

    # Static files
    import webserver.static_manager
    static_manager.read_manifest()

    # Template utilities
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.filters['make_static_path'] = static_manager.get_file_path

    # Blueprints
    from webserver.views.main import main_bp
    app.register_blueprint(main_bp)

    return app
