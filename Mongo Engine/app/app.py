from flask import Flask, Blueprint
import os
from dotenv import load_dotenv
from config import app_config
from app.routes import v1
from app.errors import init_error_handeler
from flask_cors import CORS
import  app.dashbards.dashRoutes as dashRoutes


def createApp():
    app = Flask(__name__, template_folder='../templates', static_folder='../static/')
    UPLOAD_FOLDER = os.path.join('../app/', '../static/')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    load_dotenv(".env", verbose=True)
    print(os.environ.get("APP_CONFIG", "production"))
    app.config.from_object(app_config[os.environ.get("APP_CONFIG", "production")])

    init_error_handeler(app)
    CORS(app, resources={r'/*': {'origins': '*'}})
    return app


def init_app():
    app = createApp()
    dashRoutes.init_dashRoutes(app)
    for blueprint in vars(v1).values():
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint, url_prefix="/Robonews/v1")
    return  app

app = init_app()