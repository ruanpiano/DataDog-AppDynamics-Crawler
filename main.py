from datadog import initialize, api
from requests.auth import HTTPBasicAuth
import json
import requests
import pprint
import time
import os
import stringcase
import itertools

# DataDog Configuration
options = {
	'api_key': os.getenv('DD_API_KEY'),
	'app_key': os.getenv('DD_APP_KEY')
}
initialize(**options)

# AppDynamics Configuration
APPD_PROTOCOL = os.getenv('APPD_PROTOCOL')
APPD_CONTROLLER = os.getenv('APPD_CONTROLLER')
APPD_FORMAT = os.getenv('APPD_FORMAT')
APPD_USER = os.getenv('APPD_USER')
APPD_PASS = os.getenv('APPD_PASS')
DEBUG = os.getenv('DEBUG')

def get_applications():
    r = requests.get(url = APPD_PROTOCOL+APPD_CONTROLLER+'/controller/rest/applications'+APPD_FORMAT,
                     auth=HTTPBasicAuth(APPD_USER, APPD_PASS))
    dataset = r.json()
    return dataset

def get_business_transactions(application):
    r = requests.get(url = APPD_PROTOCOL+APPD_CONTROLLER+'/controller/rest/applications/'+str(application['id'])+'/business-transactions/'+APPD_FORMAT,
                     auth=HTTPBasicAuth(APPD_USER, APPD_PASS))
    dataset = r.json()
    return dataset

def get_application_average_response_time(application):
    metric = "metric-data?metric-path=Overall%20Application%20Performance%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins=1"
    # ECommerce_E2E/metric-data?metric-path=Overall%20Application%20Performance%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins=15
    r = requests.get(url = APPD_PROTOCOL+APPD_CONTROLLER+'/controller/rest/applications/'+str(application['id'])+'/'+metric+APPD_FORMAT.replace('?', '&'),
                     auth=HTTPBasicAuth(APPD_USER, APPD_PASS))
    dataset = r.json()
    tags = []
    tags.append("application.name:"+str(application["name"]))
    tags.append("application.id:"+str(application["id"]))
    tags.append("controller:"+str(APPD_CONTROLLER))
    return dataset, tags, "appdynamics.application_average_response_time"

def get_bt_average_response_time(application, bt):
    metric = "metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C"+str(bt['tierName'])+"%7C"+str(bt['name'])+"%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins=1"
    # /controller/rest/applications/Streama/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7CJava%7C%2Fdash%2FlistGenres.json%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins=60
    r = requests.get(url = APPD_PROTOCOL+APPD_CONTROLLER+'/controller/rest/applications/'+str(application['id'])+'/'+metric+APPD_FORMAT.replace('?', '&'),
                     auth=HTTPBasicAuth(APPD_USER, APPD_PASS))
    dataset = r.json()
    tags = []
    tags.append("application.name:"+str(application["name"]))
    tags.append("application.id:"+str(application["id"]))
    tags.append("tier.name:"+str(bt['tierName']))
    tags.append("tier.id:"+str(bt['tierId']))
    tags.append("business_transaction.name:"+str(bt['name']))
    tags.append("business_transaction.internal_name:"+str(bt['internalName']))
    tags.append("business_transaction.id:"+str(bt['id']))
    tags.append("entry_point_type:"+str(bt['entryPointTypeString']))
    tags.append("controller:"+str(APPD_CONTROLLER))
    return dataset, tags, "appdynamics.business_transaction_average_response_time"

def post_datadog(dataset, tags, metric_name):
    if (dataset[0]['metricName'] != 'METRIC DATA NOT FOUND'):
        metric = stringcase.snakecase(dataset[0]['metricPath'].replace("|","")).replace("__","_")
        for tag in tags:
            metric = metric.replace(tag.split(":")[1].lower(),"")
            metric = metric.replace(stringcase.snakecase(tag.split(":")[1]),"")
        metric = metric.replace("__","_")
        for result in dataset[0]['metricValues'][0]:
            if result in {'value', 'min', 'max', 'sum', 'count', 'standardDeviation'}:
                response = api.Metric.send(metric=metric_name+"."+result, points=dataset[0]['metricValues'][0][result], tags=tags)
                if (DEBUG): print (response)
    return 0

def post_applications(applications):
    for application in applications():
        if (application['name'] != '') or (not DEBUG):
            # Get Application Average Response Time
            dataset, tags, metric_name = get_application_average_response_time(application)
            #if (DEBUG): print (dataset)
            if not (len(dataset) > 0):
                continue
            post_datadog(dataset, tags, metric_name)
            
            # Get Average Response Tiem for each Business Transaction
            dataset = get_business_transactions(application)
            if not (len(dataset) > 0):
                continue
            for bt in dataset:
                sub_dataset, tags, metric_name = get_bt_average_response_time(application,bt)
                if not (len(sub_dataset) > 0):
                    continue
                if (bt['internalName'] == '_APPDYNAMICS_DEFAULT_TX_'):
                    continue
                post_datadog(sub_dataset, tags, metric_name)
                
    
def main(): 
    post_applications(get_applications)
            
main()