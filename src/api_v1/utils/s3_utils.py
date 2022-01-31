import io
from urllib.parse import urlparse
import numpy as np
from datetime import timedelta, datetime
import boto3
from botocore.exceptions import ClientError


class S3:
    def __init__(self, date, bucket_name, access_key, secret_key, session_token, region_name):
        self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        self.path = self.create_filepath_from_date()[0]
        self.filepath = self.create_filepath_from_date()[1]
        self.s3_uri = f"s3://{bucket_name}/{self.filepath}"
        self.bucket_name = bucket_name
        self.client = boto3.client("s3", 
                                   aws_access_key_id=access_key, 
                                   aws_secret_access_key=secret_key, 
                                   aws_session_token=session_token,
                                   region_name=region_name)

    def create_filepath_from_date(self):
        first_day_of_the_week =  self.date - timedelta(days=self.date.weekday() % 7)
        year = first_day_of_the_week.year
        month = first_day_of_the_week.month
        day = first_day_of_the_week.day
        path = f"{year}/{month}/"
        filepath = f"{year}/{month}/{day}.npy"
        return path, filepath

    def check_if_file_exists(self):
        try:
            s3 = self.client
            s3.head_object(Bucket=self.bucket_name, Key=self.filepath)
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True

    def load_state_matrix(self, s3_uri=None):
        if not s3_uri: s3_uri = self.s3_uri
        bytes_ = io.BytesIO()
        parsed_s3 = urlparse(s3_uri)
        self.client.download_fileobj(
            Fileobj=bytes_, Bucket=parsed_s3.netloc, Key=parsed_s3.path[1:]
        )
        bytes_.seek(0)
        return np.load(bytes_)

    def create_directory_path(self):
        self.client.put_object(Bucket=self.bucket_name, Key=self.path)

    def load_previous_state_matrix(self):
        # create directory path
        self.create_directory_path()

        # get last week
        first_day_of_the_week =  self.date - timedelta(days=self.date.weekday() % 7)
        last_week = first_day_of_the_week - timedelta(days=7)
        year = last_week.year
        month = last_week.month
        day = last_week.day

        filepath = f"{year}/{month}/{day}.npy"
        s3_uri = f"s3://{self.bucket_name}/{filepath}"
        state_matrix = self.load_state_matrix(s3_uri)
        return state_matrix

    def upload_state_matrix(self, state_matrix, s3_uri=None):
        if not s3_uri: s3_uri = self.s3_uri
        bytes_ = io.BytesIO()
        np.save(bytes_, state_matrix)
        bytes_.seek(0)
        parsed_s3 = urlparse(s3_uri)
        self.client.upload_fileobj(
            Fileobj=bytes_, Bucket=parsed_s3.netloc, Key=parsed_s3.path[1:]
        )
        return True