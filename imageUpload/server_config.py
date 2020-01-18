import os
from pathlib import Path
import logging
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.handler import LogstashFormatter
import platform
import psutil

# APP_ROOT = Path(__file__).resolve().parent
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# DEFAULT_UPLOAD_FOLDER = Path("media/users/")
# DEFAULT_DOWNLOADS_FOLDER = Path("media/downloads/")

# IMPORT ENV VARIABLES
# config_path = APP_ROOT / "config_environment.py"
# config_path_template = APP_ROOT / "TEMPLATE_config_environment.py"
config_path = os.path.join(APP_ROOT, "config_environment.py")
config_path_template = os.path.join(APP_ROOT, "TEMPLATE_config_environment.py")



# Sending loggs to logit.io
# Create the logger and set it's logging level
logger_logit = logging.getLogger("logstash")
logger_logit.setLevel(logging.ERROR)        
# Create the handler
handler = AsynchronousLogstashHandler(
    host='fc652908-5b50-4887-8af2-89286e6febe1-ls.logit.io', 
    port=17326, 
    ssl_enable=True, 
    ssl_verify=False,
    database_path='')
# Here you can specify additional formatting on your log record/message
formatter = LogstashFormatter(message_type='python-logstash',
    extra_prefix='extra',
    extra=dict(mikrostoritev='imageUpload', okolje='production'))
handler.setFormatter(formatter)
# Assign handler to the logger
logger_logit.addHandler(handler) 

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

    LOGGER = logger_logit


class TestingConfig(Config):
    TESTING = True
