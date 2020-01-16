from imageUpload.server import app
from imageUpload.server import aws_s3_client as s3
from imageUpload.server import dropbox_client as dbx
from flask import (
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
    jsonify,
    g,
    make_response,
)
import jwt
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import requests
from io import BytesIO
from PIL import Image
import os
import json
from datetime import datetime
from functools import wraps


def jwt_token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):

        if "jwt_token" not in session:
            return jsonify({"message": "Auth token is missing!"}), 403

        token = session["jwt_token"]

        if not token:
            return jsonify({"message": "Unknown token type!"}), 403

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            g.user_info = data
            app.logger.info("Logged in user: %s", g.user_info["username"])
            app.config["LOGGER"].info("Logged in user: %s", g.user_info["username"])
        except:
            return jsonify({"message": "Token is invalid!"}), 403

        return func(*args, **kwargs)

    return decorated


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
    upload_file_size = len(upload_file) // 1024  # size in kB

    img = Image.open(BytesIO(image_binary))

    in_mem_file = BytesIO()
    img.save(in_mem_file, format=img.format)
    in_mem_file.seek(0)

    return FileStorage(
        stream=in_mem_file,
        filename=upload_file_name,
        content_type=upload_file_content_type,
        content_length=upload_file_size,
    )


@app.route("/")
def index():
    app.logger.info("New user connected")
    app.config["LOGGER"].info("New user connected")
    response = jsonify(Hello="world!!!")
    return response

@app.route("/health/liveness")
def liveness():
    healthStatus = None
    if "consul_server" in app.config and app.config["consul_server"] is not None:
        index = None
        index, data = app.config["consul_server"].kv.get("imageUpload/alive", index=index)
        if data is not None:
            healthStatus = data["Value"]
        else:
            healthStatus = "true"
    else:
        healthStatus = "true"

    if "false" in str(healthStatus).lower():
        response = jsonify(
        service_status="FAIL",
        service_code=503)
        return response, 503
    else:
        response = jsonify(
        service_status="PASS",
        service_code=200)
        return response, 200
    
@app.route("/health/readiness")
def readiness():
    healthStatus = None
    if "consul_server" in app.config and app.config["consul_server"] is not None:
        index = None
        index, data = app.config["consul_server"].kv.get("imageUpload/ready", index=index)
        if data is not None:
            healthStatus = data["Value"]
        else:
            healthStatus = "true"
    else:
        healthStatus = "true"

    if "false" in str(healthStatus).lower():
        response = jsonify(
        service_status="FAIL",
        service_code=503)
        return response, 503
    else:
        response = jsonify(
        service_status="PASS",
        service_code=200)
        return response, 200    
        
            


@app.route("/demo/info", methods=["GET"])
def demo_info_milestone_1():
    json_info = {
        "clani": ["mb2551", "rt0875"],
        "opis_projekta": "Najin projekt implementira portal za hranjenje, urejanje in deljenje fotografij",
        "mikrostoritve": ["http://34.77.38.10:5000/upload", "http://35.190.207.89:5001/images"],
        "github": [
            "https://github.com/Squad42/ImageUpload",
            "https://github.com/Squad42/ImageCatalogue",
        ],
        "travis": [
            "https://travis-ci.org/Squad42/ImageUpload",
            "https://travis-ci.org/Squad42/ImageCatalogue",
        ],
        "dockerhub": [
            "https://hub.docker.com/repository/docker/slosquad42/image_upload",
            "https://hub.docker.com/repository/docker/slosquad42/image_catalogue",
        ],
    }
    return json.dumps(json_info, indent=2), 200


@app.route("/upload")
def upload_service():
    app.logger.info("Status report: Upload service")
    app.config["LOGGER"].info("Status report: Upload service")
    response = jsonify(
        service_status="Upload service running",
        service_code=200,
        gui_gateway="/landing_page",
        api_gateways=[
            "/upload/files/<string:service>/<string:version>/",
            "/upload/urls/<string:service>/<string:version>/",
        ],
    )
    return response, 200


@app.route("/landing_page")
def landing_page():
    app.logger.info("Displaying landing page")
    app.config["LOGGER"].info("Displaying landing page")
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
        app.config["LOGGER"].error("Exception caught uploading to S3: %s", e)
        # return e
        return "Failed"
    return "{}{}".format(app.config["S3_LOCATION"], image_file.filename)


def upload_file_to_dbx(image_file, bucket_name, acl="public-read"):
    try:
        dropbox_dest = "/" + str(image_file.filename)
        metadata = dbx.files_upload(image_file.read(), dropbox_dest)
        file_url = dbx.sharing_create_shared_link(metadata.path_lower).url
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        app.logger.info("Exception caught uploading to Dropbox: %s", e)
        app.config["LOGGER"].error("Exception caught uploading to Dropbox: %s", e)
        # return e
        return "Failed"
    return file_url


# TODO: move service credential checks from each to single point check
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
        app.config["LOGGER"].info(
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
                if s3 is None:
                    response = jsonify(service_status="Missing aws credentials!", service_code=401,)
                    return response, 200

                file_url = upload_file_to_s3(upload_file, app.config["S3_BUCKET"])
                upload_service = "Amazon S3"

            if service == "dbx" and version == "v2":
                if dbx is None:
                    response = jsonify(
                        service_status="Missing dropbox credentials!", service_code=401,
                    )
                    return response, 200
                file_url = upload_file_to_dbx(upload_file, "defaut_bucket")
                upload_service = "Dropbox"

            # TODO: instead check on upload success
            if "http" in file_url:

                try:
                    user_id = int(os.environ.get("USER_ID"))
                    os.environ["USER_ID"] = str(user_id + 1)

                    db_ip = os.environ["CATALOGUE_HOSTNAME"]
                    db_port = os.environ["CATALOGUE_PORT"]

                    catalogue_api_add = "http://" + db_ip + ":" + db_port + "/images/add"
                    headers = {"Content-type": "application/json", "Accept": "text/plain"}
                    data = {
                        "user_id": user_id,
                        "service": upload_service,
                        "img_uri": str(file_url),
                        "created_datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "private": False,
                    }

                    r = requests.post(catalogue_api_add, headers=headers, data=json.dumps(data))
                    app.logger.info(
                        "Added user %s's img-uri entry to catalogue database: %s",
                        str(user_id),
                        str(file_url),
                    )
                    app.config["LOGGER"].info(
                        "Added user %s's img-uri entry to catalogue database: %s",
                        str(user_id),
                        str(file_url),
                    )
                except Exception as e:
                    print("Error saving URL upload entry to database: ", e)
                    response = jsonify(
                        service_status="Catalogue image service temporarily unavailable! Try again in a few moments.",
                        service_code=503,
                    )
                    return response, 200

            # return str(file_url)
            response = jsonify({"File url": file_url, "Upload service": upload_service})
            app.logger.info("File url %s  |  Upload service: %s", file_url, upload_service)
            app.config["LOGGER"].info("File url %s  |  Upload service: %s", file_url, upload_service)
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
        app.config["LOGGER"].info("URL received: %s", url)

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
        app.config["LOGGER"].info(
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
                if s3 is None:
                    response = jsonify(service_status="Missing aws credentials!", service_code=401,)
                    return response, 200
                file_url = upload_file_to_s3(upload_file, app.config["S3_BUCKET"])
                upload_service = "Amazon S3"

            if service == "dbx" and version == "v2":

                if dbx is None:
                    response = jsonify(
                        service_status="Missing dropbox credentials!", service_code=401,
                    )
                    return response, 200

                file_url = upload_file_to_dbx(upload_file, "defaut_bucket")
                upload_service = "Dropbox"

            # return str(file_url)
            response = jsonify({"File url": file_url, "Upload service": upload_service})
            app.logger.info("File url %s  |  Upload service: %s", file_url, upload_service)
            app.config["LOGGER"].info("File url %s  |  Upload service: %s", file_url, upload_service)
            return response
    else:
        return redirect("/"), 503


@app.route("/unprotected")
def unprotected():
    return "UNPROTECTED LINK"


@app.route("/protected")
@jwt_token_required
def protected():
    return "PROTECTED - TOKEN ONLY "
