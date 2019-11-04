from flask import Flask
import boto3
import dropbox

app = Flask(__name__)
app.config.from_object("server_config.DevelopmentConfig")

aws_s3_client = boto3.client(
    "s3", aws_access_key_id=app.config["S3_KEY"], aws_secret_access_key=app.config["S3_SECRET"]
)

dropbox_client = dropbox.Dropbox(app.config["DBX_ACCESS_TOKEN"])

from server_views import *

if __name__ == "__main__":

    # MIGHT COME HANDY FOR TESTING
    # if not app.config["UPLOAD_FOLDER"].exists():
    #     app.config["UPLOAD_FOLDER"].mkdir(parents=True)

    app.run()
