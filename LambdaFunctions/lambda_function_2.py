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


# call the bot
def lexCaller(bot, message):
    words = message.split()
    tags = []
    for word in words:
        response = bot.post_text(
            botName='album',
            botAlias='album_zero',
            userId='NoGoogleCloud',
            sessionAttributes={
                'string': 'string'
            },
            requestAttributes={
                'string': 'string'
            },
            inputText=word
        )
        if "slots" in response:
            tags.append(response["slots"]["animals"])
        else:
            tags.append(word)
    return tags



## connect to Elastic Search
def connectES(host):
    return Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = HTTPBasicAuth('master', 'Abc@123456'),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        timeout=30
    )


## search ES
def searchES(labels, es):
    # build the query
    query = {
        "size": 10,
        "query": {
            "terms": {
                "labels": labels
            }
        }
    }
    
    # TODO: try except to catch error
    # randomly return 3 ids
    search_results = es.search(index="photos", body=query)
    urls = []
    if search_results:
        entities = search_results["hits"]["hits"]
        for entity in entities:
            url = "https://voice-controlled-album.s3.amazonaws.com/"
            urls.append(url+entity["_source"]["ObjectKey"])
    
    return urls


""" --- Main handler --- """"""---ok"""


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    # return {
    #     "statusCode": 200,
    #     "body": event["queryParams"]['q'] #event["body"]["queryParams"]["q"]
    # }
    # bot = boto3.client("lex-runtime")
    # return lexCaller(bot, "cat faslfj")
    newMessage = event["queryParams"]['q']
        
    bot = boto3.client("lex-runtime")
    response = lexCaller(bot, newMessage)
    
    if isinstance(response, str):
        responseMessages = buildUnstructuredResponse(response)
    
        if (len(responseMessages) == 0):
            responseMessages = buildUnstructuredResponse("Sorry, I do not understand.")
        
        return {
            "statusCode": 500,
            "messages": responseMessages
        }
    
    host = "search-album-wfofr7z7fjewlog2wnub7pecae.us-east-1.es.amazonaws.com"
    if response:
        es = connectES(host)
        fname = "dogtest.jpg"
        # s3 = boto3.client("s3")
        # album = 'voice-controlled-album'
        # return getImage(fname, album, s3)
        return {
            "statusCode":200,
            "results": searchES(response, es)
        }
    else:
        return {
            "statusCode": 403,
            "results": []
        }
