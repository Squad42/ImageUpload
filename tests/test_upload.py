import pytest
from urllib import request
from imageUpload.server import *
from imageUpload.server_views import upload_file_to_s3

#class Test_Amazon_S3:
	
def test_imageUpload():
	with open('tests/test_resouces/test.jpg','rb') as upload_file:
		upload_file.filename='test.jpg'
		upload_file.content_type='image/jpg'
		s3_file_url = upload_file_to_s3(upload_file, app.config["S3_BUCKET"])
	assert "amazonaws.com/test.jpg" in s3_file_url

def test_dockerflaskapp_helloworld():
	response = request.urlopen('http://0.0.0.0:5000')
	html = response.read()
	assert "{\"Hello\":\"world\"}" in html
