"""Flask application factory and global error handlers."""

from __future__ import annotations

from pathlib import Path
from flask import Flask

from app.api import error_response
from app.config import get_settings
from utils.logger import configure_logging


def create_app():
    """Create and configure the Flask application instance."""
    project_root = Path(__file__).resolve().parent.parent
    settings = get_settings()
    configure_logging(settings.log_level)

    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    
    from app.routes import main
    app.register_blueprint(main)

    @app.errorhandler(400)
    def handle_bad_request(error):
        return error_response("Bad request.", code="bad_request", status_code=400)

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response("The requested resource was not found.", code="not_found", status_code=404)

    @app.errorhandler(500)
    def handle_server_error(error):
        return error_response("An internal server error occurred.", code="internal_error", status_code=500)

    return app