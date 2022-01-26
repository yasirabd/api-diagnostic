import io
from urllib.parse import urlparse
import numpy as np
from datetime import timedelta, datetime
import boto3


class S3:
    def __init__(self, date, bucket_name, access_key, secret_key, region_name):
        self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        self.path = self.create_filepath_from_date()[0]
        self.filepath = self.create_filepath_from_date()[1]
        self.s3_uri = f"s3://{bucket_name}/{self.filepath}"
        self.bucket_name = bucket_name
        self.session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region_name)
        self.s3_resource = self.session.resource('s3')

    def create_filepath_from_date(self):
        first_day_of_the_week =  self.date - timedelta(days=self.date.weekday() % 7)
        year = first_day_of_the_week.year
        month = first_day_of_the_week.month
        day = first_day_of_the_week.day
        path = f"{year}/{month}/"
        filepath = f"{year}/{month}/{day}.npy"
        return path, filepath

    def check_if_file_exists(self):
        obj = list(self.s3_resource.Bucket(self.bucket_name).objects.filter(Prefix=self.filepath))
        if len(obj) > 0 and obj[0].key == self.filepath:
            return True
        else:
            return False

    def load_state_matrix(self, s3_uri=None):
        if not s3_uri: s3_uri = self.s3_uri
        bytes_ = io.BytesIO()
        parsed_s3 = urlparse(s3_uri)
        client = self.session.client('s3')
        client.download_fileobj(
            Fileobj=bytes_, Bucket=parsed_s3.netloc, Key=parsed_s3.path[1:]
        )
        bytes_.seek(0)
        return np.load(bytes_)

    def create_directory_path(self):
        client = self.session.client('s3')
        client.put_object(Bucket=self.bucket_name, Key=self.path)

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
        client = self.session.client('s3')
        bytes_ = io.BytesIO()
        np.save(bytes_, state_matrix)
        bytes_.seek(0)
        parsed_s3 = urlparse(s3_uri)
        client.upload_fileobj(
            Fileobj=bytes_, Bucket=parsed_s3.netloc, Key=parsed_s3.path[1:]
        )
        return True