from flask import Flask,request,redirect
import boto3
from werkzeug import secure_filename
#from .config import Config,TestConfig
#pip install flask boto3
#import config



app = Flask(__name__)    
#app.config.from_object(config)
app.config.from_pyfile('config.py')
s3 = boto3.client("s3",
                  aws_access_key_id=app.config['S3_KEY'],
                  aws_secret_access_key=app.config['S3_SECRET'])




def token2username(auth_token:int) -> str:
    '''
    :param auth_token: authentication token sent by user in http request.
    
    :returns: username
    ''' 
    #testno - popravi
    return "user1"

def upload_file_to_s3(file, bucket_name, acl="public-read"):

    try:
        
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
        '''
        s3.put_object(Body=file,
                      Bucket=bucket_name,
                      Key=secure_filename(file.filename),
                      ContentType=file.mimetype)
        '''
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("EXXXXXCEPTION: Something Happened: ", e)
        return e 
    return "{}{}".format(app.config["S3_LOCATION"], file.filename)

@app.route('/')
def index():
    return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title></title>
            </head>
            <body>
            
                <h1>Upload Your Files Bro</h1>
            
                <form action="/file" method="POST" enctype="multipart/form-data">
            
                    <label for="user_file">Upload Your File</label>
                    <br></br>
                    <input type="file" name="user_file">
                    <br></br>
                    <button type="submit">Upload</button>
            
                </form>
            
            </body>
            
            </html>
            '''

@app.route('/file', methods=['POST'])
def uploadAsFile():
    #Handle authentication: check user authentication token
    #Check header for Content-Lenght field if file size restriction is respected
    #Check the actual file size
    #Store file with Amazon S3 or similar service
    #Create new catalogue record connecting user with newly stored image
    
    """
    if not "Authentication" in request.args or not request.args['Authentication']:
        return("Forbidden! User not authenticated!") 
    else:
        username = token2username(request.args['Authentication'])
    """    
    if request.method == 'POST':
        if 'Content-Length' in request.args and\
            request.args['Content-Length']>app.config['FILE_SIZE_LIMIT']:
            return "File too big to upload.."
        if "user_file" not in request.files:
            return "No files uploaded!"
        file = request.files['user_file']
        print("!!!!!!REQUEST MIMETYPE:",request.mimetype)
        print("!!!!!!FILENAME:",file.filename)
        print("!!!!!!CONTENT TYPE:",file.content_type)
        print("!!!!!!CONTENT LENGTH:",file.content_length)
        print("!!!!!!MIMETYPE:",file.mimetype)
        print("IF FILE?",file)
        if file:
            file_url = upload_file_to_s3(file,app.config['S3_BUCKET'])
            return str(file_url)
    else:
        return redirect('/')
        #return("Unsupported HTTP method..")
    
@app.route('/url', methods=['POST'])
def uploadAsURL():
    #Handle authentication: check user authentication token
    #Check header for Image_url field
    #Check validity of Image_url
    #Create new catalogue record connecting user with new image url
    
    if not request.args['Authentication']:
        return("Forbidden! User not authenticated!") 
    else:
        username = token2username(request.args['Authentication'])
    
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()    
    
    