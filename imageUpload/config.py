import os
#import config_environment
exec(open("./config_environment.py").read())

FILE_SIZE_LIMIT = 25000;

#SERVER_NAME = '192.168.2.100'
UPLOAD_SERVICE_ADDRESS = '192.168.2.100'

CATALOGUE_SERVICE_ADDRESS = '192.168.2.101'
SHARING_SERVICE_ADDRESS = '192.168.2.102'
PROCESSING_SERVICE_ADDRESS = '192.168.2.103'
ANALYSIS_SERVICE_ADDRESS = '192.168.2.104'
COMMENTSANDLIKES_SERVICE_ADDRESS = '192.168.2.105'

S3_BUCKET                 = os.environ.get("S3_BUCKET")
S3_KEY                    = os.environ.get("S3_KEY")
S3_SECRET                 = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY                = os.urandom(32)
DEBUG                     = True
PORT                      = 5000
