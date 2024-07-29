import os
import firebase_admin
from firebase_admin import credentials, storage

from . import base
from . import data

REMOTE_REFS_BASE = 'refs/heads/'
LOCAL_REFS_BASE = 'refs/remote/'


def push (name,branch):
    cred = credentials.Certificate('path/to/your/private-key.json file')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'your storage bucket name...!'  # Ensure this is just the bucket name without 'gs://'
    })

    if branch=='master' :
        current_directory = os.getcwd()
        delete_directory(name,os.path.basename(current_directory))
        upload_directory_to_firebase(name,current_directory, os.path.basename(current_directory))
    else:
        print('Push through the master branch...!')


def upload_directory_to_firebase(name,local_path, bucket_path=""):
    for root, dirs, files in os.walk(local_path):
        rel_path = os.path.relpath(root, local_path)
        if rel_path == '.':
            rel_path = ''

        bucket = storage.bucket()

        for file in files:
            local_file_path = os.path.join(root, file)
            firebase_storage_path =f'{name} / ' + os.path.join(bucket_path, rel_path, file).replace("\\", "/")
            print(firebase_storage_path)
            blob = bucket.blob(firebase_storage_path)
            blob.upload_from_filename(local_file_path)
            print(f'File {local_file_path} uploaded to {firebase_storage_path}.')


def delete_directory(name,directory_name):
    directory_path = f"{name} / {directory_name}/"
    
    try:
        bucket=storage.bucket()
        blobs = list(bucket.list_blobs(prefix=directory_path))
        
        if not blobs:
            print(f"No files found in the directory {directory_path}")
            return
            
        for blob in blobs:
            blob.delete()
            print(f"Deleted {blob.name}")
        
        print(f"Directory {directory_path} deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
