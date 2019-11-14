from imageUpload.server import app
from imageUpload.server import aws_s3_client as s3
from imageUpload.server import dropbox_client as dbx
from flask import flash, redirect, render_template, request, send_from_directory, session, url_for, jsonify
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
import requests
from io import BytesIO
from PIL import Image


def allowed_file(filename):
    return (
        "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def token2username(auth_token: int) -> str:
    """
    :param auth_token: authentication token sent by user in http request.
    
    :returns: username
    """
    # testno - popravi
    return "user1"


def url_image_to_FileStorage(url, image_binary):

    # upload_file = image
    upload_file = image_binary
    upload_file_type = url.split(".")[-1]
    upload_file_name = url.split("/")[-1]
    upload_file_content_type = "image/" + upload_file_type
    upload_file_size = len(upload_file) // 1024    # size in kB

    img = Image.open(BytesIO(image_binary))

    in_mem_file = BytesIO()
    img.save(in_mem_file, format=img.format)
    in_mem_file.seek(0)

    return FileStorage(stream=in_mem_file, filename=upload_file_name, content_type=upload_file_content_type, content_length=upload_file_size)

@app.route("/")
def index():
    app.logger.info("New user connected")
    response = jsonify(Hello="world")
    return response

@app.route("/landing_page")
def landing_page():
    app.logger.info("Displaying landing page")
    return render_template("index.html")

def upload_file_to_s3(image_file, bucket_name, acl="public-read"):
    try:

        s3.upload_fileobj(
            image_file,
            bucket_name,
            image_file.filename,
            ExtraArgs={"ACL": acl, "ContentType": image_file.content_type},
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        app.logger.info("Exception caught uploading to S3: %s", e)
        return e
    return "{}{}".format(app.config["S3_LOCATION"], image_file.filename)


def upload_file_to_dbx(image_file, bucket_name, acl="public-read"):
    try:
        dropbox_dest = "/" + str(image_file.filename)
        metadata = dbx.files_upload(image_file.read(), dropbox_dest)
        file_url = dbx.sharing_create_shared_link(metadata.path_lower).url
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        app.logger.info("Exception caught uploading to Dropbox: %s", e)
        return e
    return file_url


# TODO: possible merge of upload functions
# @user.route("/upload/<file_type>/<url>/<service>/<version>/", defaults={"url": None})
@app.route("/upload/files/<string:service>/<string:version>/", methods=["POST"])
def upload_image(service, version):
    # Handle authentication: check user authentication token
    # Check header for Content-Lenght field if file size restriction is respected
    # Check the actual file size
    # Store file with Amazon S3 or similar service
    # Create new catalogue record connecting user with newly stored image

    """
    if not "Authentication" in request.args or not request.args['Authentication']:
        return("Forbidden! User not authenticated!") 
    else:
        username = token2username(request.args['Authentication'])
    """

    if request.method == "POST":

        if "user_image" not in request.files:
            # return "No file uploaded!"
            return jsonify(message="No file uploaded"), 204

        upload_file = request.files["user_image"]

        if upload_file.filename == "":
            # return "Empty file path!"
            return jsonify(message="Empty file path"), 204

        if (
            "Content-Length" in request.args
            and request.args["Content-Length"] > app.config["FILE_SIZE_LIMIT"]
        ):
            # return "File too big to upload.."
            return jsonify(message="File size too large for upload."), 413

        app.logger.info(
            "\n\n\t============ UPLOAD iNFO ============ \nFile %s ||| Filename: %s  || Size: %s \nContent-type: %s || Mime-type %s \nFile-type: %s \n =========================\n"
            % (
                upload_file,
                upload_file.filename,
                upload_file.content_length,
                upload_file.content_type,
                upload_file.mimetype,
                type(upload_file),
            )
        )

        if upload_file and allowed_file(upload_file.filename):

            upload_file.filename = secure_filename(upload_file.filename)
            file_url = ""

            if service == "aws" and version == "v1":
                file_url = upload_file_to_s3(upload_file, app.config["S3_BUCKET"])
                upload_service = "Amazon S3"

            if service == "dbx" and version == "v2":
                file_url = upload_file_to_dbx(upload_file, "defaut_bucket")
                upload_service = "Dropbox"

            # return str(file_url)
            response = jsonify({"File url": file_url, "Upload service": upload_service})
            app.logger.info("File url %s  |  Upload service: %s", file_url, upload_service)
            return response
    else:
        return redirect("/"), 503
        # return("Unsupported HTTP method..")


@app.route("/upload/urls/<string:service>/<string:version>/", methods=["POST"])
def upload_image_url(service, version):
    # Handle authentication: check user authentication token
    # Check header for Content-Lenght field if file size restriction is respected
    # Check the actual file size
    # Store file with Amazon S3 or similar service
    # Create new catalogue record connecting user with newly stored image

    """
    if not "Authentication" in request.args or not request.args['Authentication']:
        return("Forbidden! User not authenticated!") 
    else:
        username = token2username(request.args['Authentication'])
    """

    if request.method == "POST":

        if "image_url" not in request.json:
            return jsonify(message="Missing image url!"), 400

        url = request.json["image_url"]
        app.logger.info("URL received: %s", url)
        
        if url == "" or url is None:
            return jsonify(message="Empty file path"), 204

        # fetch the image
        try:
            response_image_url = requests.get(url)
            image_binary = response_image_url.content
            upload_file = url_image_to_FileStorage(url, image_binary)
        except Exception as e:
            return jsonify(message=e), 400

        if upload_file.content_length > app.config["FILE_SIZE_LIMIT"]:
            # return "File too big to upload.."
            return jsonify(message="File size too large for upload."), 413

        app.logger.info(
            "\n\n\t============ UPLOAD iNFO ============ \nFile %s ||| Filename: %s  || Size: %s \nContent-type: %s || Mime-type %s \nFile-type: %s \n =========================\n"
            % (
                upload_file,
                upload_file.filename,
                upload_file.content_length,
                upload_file.content_type,
                upload_file.mimetype,
                type(upload_file),
            )
        )

        if upload_file and allowed_file(upload_file.filename):

            upload_file.filename = secure_filename(upload_file.filename)
            file_url = ""

            if service == "aws" and version == "v1":
                file_url = upload_file_to_s3(upload_file, app.config["S3_BUCKET"])
                upload_service = "Amazon S3"

            if service == "dbx" and version == "v2":
                file_url = upload_file_to_dbx(upload_file, "defaut_bucket")
                upload_service = "Dropbox"

            # return str(file_url)
            response = jsonify({"File url": file_url, "Upload service": upload_service})
            app.logger.info("File url %s  |  Upload service: %s", file_url, upload_service)
            return response
    else:
        return redirect("/"), 503
