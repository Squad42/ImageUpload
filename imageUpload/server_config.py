import os
from pathlib import Path

# APP_ROOT = Path(__file__).resolve().parent
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# DEFAULT_UPLOAD_FOLDER = Path("media/users/")
# DEFAULT_DOWNLOADS_FOLDER = Path("media/downloads/")

# IMPORT ENV VARIABLES
# config_path = APP_ROOT / "config_environment.py"
# config_path_template = APP_ROOT / "TEMPLATE_config_environment.py"
config_path = os.path.join(APP_ROOT, "config_environment.py")
config_path_template = os.path.join(APP_ROOT, "TEMPLATE_config_environment.py")

try:
    # if config_path.exists():
    if os.path.exists(config_path):
        exec(open(config_path).read())
    else:
        # exec(open(config_path_template).read())
        pass
except Exception as e:
    print("No configuration files found: ", e)


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "this-really-needs-to-be-changed"


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    PORT = 5000

    # upload restrictions
    ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])
    FILE_SIZE_LIMIT = 25000  # dropbox allows 150 MB, before streaming

    # MICROSERVICES NETWORK CONFIG
    UPLOAD_SERVICE_ADDRESS = "192.168.2.100"
    CATALOGUE_SERVICE_ADDRESS = "192.168.2.101"
    SHARING_SERVICE_ADDRESS = "192.168.2.102"
    PROCESSING_SERVICE_ADDRESS = "192.168.2.103"
    ANALYSIS_SERVICE_ADDRESS = "192.168.2.104"
    COMMENTSANDLIKES_SERVICE_ADDRESS = "192.168.2.105"

    # AMAZON AWS CONFIG
    S3_BUCKET = os.environ.get("S3_BUCKET")
    S3_KEY = os.environ.get("S3_KEY")
    S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")
    S3_LOCATION = "http://{}.s3.amazonaws.com/".format(S3_BUCKET)

    # DROBPOX (DBX) CONFIG
    DBX_ACCESS_TOKEN = os.environ.get("DBX_ACCESS_TOKEN")

    CATALOGUE_HOSTNAME = os.environ.get("CATALOGUE_HOSTNAME")
    CATALOGUE_PORT = os.environ.get("CATALOGUE_PORT")

    # CONFIG SERVER
    if "CONSUL_HOST" in os.environ:
    	CONFIG_HOST = os.environ["CONSUL_HOST"]
    else:
        CONFIG_HOST = "localhost"
    if "CONSUL_PORT" in os.environ:
    	CONFIG_PORT = os.environ["CONSUL_PORT"]
    else:
        CONFIG_PORT = 8500


class TestingConfig(Config):
    TESTING = True
