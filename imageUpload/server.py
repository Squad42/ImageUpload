from flask import Flask
import boto3
import dropbox
import os

app = Flask(__name__)
app.config.from_object("imageUpload.server_config.DevelopmentConfig")

try:
    aws_s3_client = boto3.client(
        "s3", aws_access_key_id=app.config["S3_KEY"], aws_secret_access_key=app.config["S3_SECRET"]
    )
except Exception as e:
    print("AWS client not established!")
    aws_s3_client = None


try:
    dropbox_client = dropbox.Dropbox(app.config["DBX_ACCESS_TOKEN"])
except Exception as e:
    print("DROPBOX client not established!")
    dropbox_client = None

from imageUpload.server_views import *

# todo: replace with user auto increment
os.environ["USER_ID"] = str(50)

if __name__ == "__main__":

    # MIGHT COME HANDY FOR TESTING
    # if not app.config["UPLOAD_FOLDER"].exists():
    #     app.config["UPLOAD_FOLDER"].mkdir(parents=True)

    app.run(host="0.0.0.0")
