import os

from dotenv import load_dotenv


class Config(object):
    """
    Common configurations
    """
    load_dotenv(".env", verbose=True)
    Mongo_DATABASE_URI = os.environ.get("DATABASE_URL")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = [
        "access",
        "refresh",
    ]


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    PROPAGATE_EXCEPTIONS = True
    UPLOADED_IMAGES_DEST = os.path.join("static", "images")  # manage root folder



class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
