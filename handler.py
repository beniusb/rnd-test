import boto3
from datetime import date, datetime
from flask import Flask, jsonify, request, abort
import json

app = Flask(__name__)
BASE_ROUTE = "/"

REGION_FILE_NAME = "regions.txt"


# Helper to translate AWS datatime to ISO format
def datetime_converter(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {} is not serializable".format(type(obj)))


def get_region_from_file():
    f = open(REGION_FILE_NAME, 'r')
    data = f.read()
    f.close()
    return data


def config_region(region_data):
    f = open(REGION_FILE_NAME, 'w+')
    f.write(region_data)
    f.close()


def get_instances(regions):
    instances_list = []
    ec2client = boto3.client('ec2', region_name=regions)
    response = ec2client.describe_instances()
    for r in response['Reservations']:
        for i in r['Instances']:
            instances_list.append(i)
    return instances_list


def etl():
    regions_name = get_region_from_file()
    print(regions_name)
    instances_list = get_instances(regions_name)
    instances_list.sort(key=lambda x: datetime_converter(x['launch_time']))
    with open(regions_name + '.json', 'w+') as f:
        json.dump(instances_list, f)


@app.route(BASE_ROUTE, methods=['GET'])
def lambda_handler(event, context):
    try:
        args = request.args
        if args and request.args.get('region'):
            region = request.args.get('region')
            config_region(region)
            etl()
            f = open(region+'json','r')
            data = json.load(f)
            return jsonify(data)
        else:
            abort(404, "the request should contain the region param")


    except:
        print("An exception occurred during the process")
