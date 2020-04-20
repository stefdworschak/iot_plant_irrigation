import zipfile
import os

import pyzipper
import boto3

import env_vars

BROKER_ADDRESS = os.environ.get('BROKER_ADDRESS', 'No value set')
S3_BASE_URL = os.environ.get('S3_BASE_URL', 'No value set')
ZIP_FILE_NAME = 'device.zip'
PK_FILE_NAME = 'private.pem.key'
CERT_FILE_NAME = 'cert.pem.crt'
AWS_CERT_NAME = 'AmazonRootCA1.pem'
KEYS_FILE_NAME = 'keys.py'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_FILE_PATH = os.path.join(BASE_DIR, 'static', 'device')
EXTRA_FILES = ['requirements.txt', 'script.py', 'sensors.py']

#S3 INFO
BUCKET =  os.environ.get('S3_BUCKET', 'No value set')
ACCESS_KEY =  os.environ.get('S3_ACCESS_KEY', 'No value set')
SECRET_KEY =  os.environ.get('S3_SECRET_KEY', 'No value set')


def add_to_zip(credentials, thing_name, password):
    keys_file = (
        "import os\n"
        + "THING_ID = '%s'\n"
        + "os.environ.setdefault('BROKER_ADDRESS', '%s')\n"
        + "os.environ.setdefault('CLIENT_ID', THING_ID)\n"
        + "os.environ.setdefault('SUBSCRIBER_TOPIC', f'$aws/things/{THING_ID}/shadow/update/accepted')\n"
        + "os.environ.setdefault('PUBLISHER_TOPIC', f'$aws/things/{THING_ID}/shadow/update')\n"
        ) % (thing_name, BROKER_ADDRESS)

    pk_content = credentials['keyPair']['PrivateKey']
    cert_content = credentials['certificatePem']
    zipfile_path = os.path.join(ZIP_FILE_PATH, ZIP_FILE_NAME)
    with open(os.path.join(ZIP_FILE_PATH, 'script.py'), 'r') as script_file:
        script = script_file.read()
    with open(os.path.join(ZIP_FILE_PATH, 'requirements.txt'), 'r') as reqs_file:
        reqs = reqs_file.read()
    with open(os.path.join(ZIP_FILE_PATH, 'sensors.py'), 'r') as sensors_file:
        sensors = sensors_file.read()
    with open(os.path.join(ZIP_FILE_PATH, 'keys', AWS_CERT_NAME), 'r') as aws_cert_file:
        aws_cert = aws_cert_file.read()

    with open(os.path.join(ZIP_FILE_PATH, 'README.MD'), 'r') as readme_file:
        readme = readme_file.read()
    readme_thing = readme.replace('{{thing_name}}', thing_name)

    with pyzipper.AESZipFile(
            zipfile_path,
            'w',
            compression=pyzipper.ZIP_LZMA,
            encryption=pyzipper.WZ_AES) as zf:
        zf.pwd = password
        zf.writestr('script.py', script)
        zf.writestr('requirements.txt', reqs)
        zf.writestr('sensors.py', sensors)
        zf.writestr('keys.py', keys_file)
        zf.writestr('Readme.MD', readme_thing)
        zf.writestr(os.path.join('keys', AWS_CERT_NAME), aws_cert)
        zf.writestr(os.path.join('keys', PK_FILE_NAME), pk_content)
        zf.writestr(os.path.join('keys', CERT_FILE_NAME), cert_content)
        zf.close()
    
    upload_to_s3(zipfile_path, thing_name)
    s3_file_url = S3_BASE_URL + thing_name + '.zip'
    return s3_file_url


def upload_to_s3(zipfile, thing_name):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    file_upload = s3.upload_file(zipfile, BUCKET, (thing_name +'.zip'), ExtraArgs={'ACL':'public-read'})
    return file_upload 

def delete_from_s3(thing_name):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    s3.delete_object(Bucket=BUCKET, Key=thing_name+'.zip')
    return True
