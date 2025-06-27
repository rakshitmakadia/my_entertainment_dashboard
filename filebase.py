import boto3
import constants
import os
from datetime import datetime, timedelta
import re


def get_latest_url_file():

    """
    Retrieves the latest URL file from the S3 bucket and saves it locally.

    Connects to the S3 bucket using credentials from the constants module.
    Lists all objects in the specified bucket, sorts them by the last modified
    date in descending order, and checks if the latest file is a text file
    containing 'link' in its name. If so, it downloads the file to a local
    directory specified in constants.BASE_FILE_PATH with a timestamp appended
    to the file name. Returns the local file path if successful, otherwise
    returns None and prints a message if no suitable file is found.

    :return: The local file path if successful, otherwise None
    """

    s3 = boto3.client(
        "s3",
        endpoint_url=constants.S3_ENDPOINT_URL,
        aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=constants.AWS_SECRET_ACCESS_KEY,
    )

    file_path = None
    res = s3.list_objects(Bucket=constants.BUCKET)["Contents"]
    res.sort(key=lambda x: x["LastModified"], reverse=True)
    object_name = res[0]["Key"]

    if object_name[-4:] == ".txt" and "link" in object_name.lower():
        file_name = (
            object_name[:-4]
            + "_"
            + res[0]["LastModified"].strftime("%Y%m%d%H%M%S")
            + ".txt"
        )
        file_path = os.path.join(constants.BASE_FILE_PATH, file_name)

        print(
            "Got the latest file: "
            + object_name
            + "; Last modified: "
            + res[0]["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
        )
        print("Saving to: " + file_path)

        with open(file_path, "wb") as f:
            s3.download_fileobj(constants.BUCKET, object_name, f)
    else:
        print("Links file not found")

    return file_path


def upload_to_folder():

    """
    Uploads all files from the local directory specified in constants.BASE_FILE_PATH to an S3 bucket.

    Connects to the S3 bucket using credentials from the constants module. For each file in 
    the local directory and its subdirectories, constructs an S3 key using the current date 
    as a prefix and uploads the file to the specified bucket. The current date prefix ensures 
    that files are organized by upload date in the bucket. If any upload fails, an error message 
    is printed with details of the failed file.

    :return: None
    """

    s3 = boto3.client(
        "s3",
        endpoint_url=constants.S3_ENDPOINT_URL,
        aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=constants.AWS_SECRET_ACCESS_KEY,
    )

    current_date_prefix = datetime.now().date().strftime("%Y%m%d") + "/"

    for root, dirs, files in os.walk(constants.BASE_FILE_PATH):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, constants.BASE_FILE_PATH)
            s3_key = os.path.join(current_date_prefix, relative_path).replace("\\", "/")
            try:
                s3.upload_file(local_path, constants.BUCKET, s3_key)
                print(f"Uploaded {local_path} to s3://{constants.BUCKET}/{s3_key}")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
    return None


def delete_folder_30days():
    """
    Deletes all objects in the specified S3 bucket that are older than 30 days.

    Connects to the S3 bucket using credentials from the constants module. Lists all objects
    in the bucket and checks if each object's key starts with a date in the format YYYYMMDD.
    If the object is older than 30 days, it is deleted from the bucket.

    :return: None
    """
    s3 = boto3.client(
        "s3",
        endpoint_url=constants.S3_ENDPOINT_URL,
        aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=constants.AWS_SECRET_ACCESS_KEY,
    )

    current_date_30 = (datetime.now() - timedelta(days=30)).date()
    try:
        response = s3.list_objects_v2(Bucket=constants.BUCKET)["Contents"]
        for obj in response:
            print("Checking object: " + obj["Key"])
            # checking if key starts with YYYYMMDD
            result = re.match(r"^\d{8}/", obj["Key"])
            if not result:
                print(
                    f"Skipping object: {obj['Key']} because it does not start with YYYYMMDD"
                )
                continue
            obj_dt = datetime.strptime(obj["Key"].split("/")[0], "%Y%m%d").date()
            if obj_dt < current_date_30:
                s3.delete_object(Bucket=constants.BUCKET, Key=obj["Key"])
                print(f"Deleted {obj['Key']}")
            else:
                print(
                    f"Skipping object: {obj['Key']} because it is not older than 30 days"
                )
    except Exception as e:
        print(f"Failed to list objects in s3://{constants.BUCKET}: {e}")

    return None


def local_tmp_cleanup():
    """
    Deletes all files in the local directory specified in constants.BASE_FILE_PATH
    and its subdirectories.

    Walks through the directory and its subdirectories, and deletes each file it
    encounters. If any deletion fails, an error message is printed with details
    of the failed file.

    :return: None
    """
    for root, dirs, files in os.walk(constants.BASE_FILE_PATH):
        for file in files:
            local_path = os.path.join(root, file)
            try:
                os.remove(local_path)
                print(f"Deleted {local_path}")
            except Exception as e:
                print(f"Failed to delete {local_path}: {e}")
    return None
