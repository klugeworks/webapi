from flask import Flask
from kluge_web.views import blue, api
import datastore
import os


def create_app(cfg_module=None, cfg_overrides=None):
    # Override hosting for default static pages and .js
    static_files = os.getenv('KLUGE_STATIC_PAGES', "./static")

    app = Flask('kluge_web', static_folder=static_files, static_url_path="/demo")
    api.init_app(app)

    # Dynamically load configuration, with potential overrides
    load_config(app, cfg_module, cfg_overrides)

    # Dynamically create datastore object and attach it to app
    app.kluge_web_datastore = create_datastore(app)

    # import all route modules
    # and register blueprints
    app.register_blueprint(blue)
    return app, api


def load_config(app, cfg_module, cfg_overrides):
    # Load a default configuration file
    app.config.from_object('kluge_web.default_settings.DevelopmentConfig')

    # Override module -- designed for use in test cases
    if cfg_module:
        app.config.from_object(cfg_module)

    # If cfg is empty try to load config file from environment variable
    app.config.from_envvar('KLUGE_WEB_SETTINGS', silent=True)

    # Apply overrides
    if cfg_overrides:
        app.config.update(cfg_overrides)


def create_datastore(app):
    # Discover datastore type from configuration
    ds_class = app.config.get('KLUGE_WEB_DATASTORE', None)
    ds_hostname = app.config.get('KLUGE_DS_HOSTNAME', None)
    ds_port = app.config.get('KLUGE_DS_PORT', None)
    redis_ds = getattr(datastore, ds_class)(hostname=ds_hostname, port=ds_port)
    return redis_ds