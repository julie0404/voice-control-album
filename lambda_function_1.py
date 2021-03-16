import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
from boto3.dynamodb.conditions import Key
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import requests
from requests.auth import HTTPBasicAuth
import json 
import random
import botocore

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


## get latest image
def latest_image(s3, album):
    # lambda function for sort files by date
    get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
    
    # get the latest image
    objs = s3.list_objects_v2(Bucket=album)["Contents"]
    latest = [(obj['Key'], obj['LastModified']) for obj in sorted(objs, key=get_last_modified)][-1]
    return (latest[0], latest[1].strftime('%Y-%m-%dT%H:%M:%S'))


## detect labels by rekognition
def rekognize_labels(photo, bucket):
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)
    labels = [info["Name"] for info in response["Labels"]]
    return labels
    
    
## get labels from 
def assemble_labels(photo, album, s3):
    labels = rekognize_labels(photo, album)   # rekognition
    customLabel = s3.head_object(Bucket=album, Key=photo)["ResponseMetadata"]["HTTPHeaders"]['x-amz-meta-customlabels']
    labels.append(customLabel)    # attach the custom label
    return labels


## connect to ES instance
def connectES(host):
    return Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = HTTPBasicAuth('master', 'Abc@123456'),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        timeout=30
    )

## index photo to ES instance
def indexES(photo, album, timeModified, labels, es):
    toStore = {
        "ObjectKey": photo,
        "bucket": album,
        "createdTimestamp": timeModified,
        "labels": labels
    }
    if not es.indices.exists(index="photos"):
        es.indices.create("photos")
    es.index(index="photos", id=photo, body=toStore)

## main handler
def lambda_handler(event, context):
    
    # path to the bucket
    s3 = boto3.client('s3')
    album = 'voice-controlled-album'
    
    # get the latest image and its upload date
    photo, timeModified = latest_image(s3, album)
    
    # detect labels from rekognition
    labels = assemble_labels(photo, album, s3)
    
    # connect to elastic search
    host = "search-album-wfofr7z7fjewlog2wnub7pecae.us-east-1.es.amazonaws.com"
    es = connectES(host)
    indexES(photo, album, timeModified, labels, es)

    return {"statusCode": 200, "response": labels}