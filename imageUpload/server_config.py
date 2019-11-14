import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
# DEFAULT_UPLOAD_FOLDER = Path("media/users/")
# DEFAULT_DOWNLOADS_FOLDER = Path("media/downloads/")

# IMPORT ENV VARIABLES
try:
	exec(open(APP_ROOT / "config_environment.py").read())
except Exception as e:
	print("Error importing environment configuration: ", e)
	print("Using default config")
	exec(open(APP_ROOT / "TEMPLATE_config_environment.py").read())

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
    SECRET_KEY = os.urandom(32)
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


class TestingConfig(Config):
    TESTING = True
