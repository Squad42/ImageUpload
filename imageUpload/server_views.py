from server import app
from server import aws_s3_client as s3
from server import dropbox_client as dbx
from flask import flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug import secure_filename


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


@app.route("/")
def index():
    app.logger.info("New user connected")
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


@app.route("/upload/<service>/<version>/files", methods=["POST"])
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
            return "No file uploaded!"

        upload_file = request.files["user_image"]

        if upload_file.filename == "":
            return "Empty file path!"

        if (
            "Content-Length" in request.args
            and request.args["Content-Length"] > app.config["FILE_SIZE_LIMIT"]
        ):
            return "File too big to upload.."

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

            if service == "dbx" and version == "v2":
                file_url = upload_file_to_dbx(upload_file, "defaut_bucket")

            return str(file_url)
    else:
        return redirect("/")
        # return("Unsupported HTTP method..")


@app.route("/url", methods=["POST"])
def uploadAsURL():
    # Handle authentication: check user authentication token
    # Check header for Image_url field
    # Check validity of Image_url
    # Create new catalogue record connecting user with new image url

    if not request.args["Authentication"]:
        return "Forbidden! User not authenticated!"
    else:
        username = token2username(request.args["Authentication"])

    if request.method == "POST":
        return do_the_login()
    else:
        return show_the_login_form()

