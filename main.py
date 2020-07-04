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

def get_application_average_response_time(application):
    metric = "metric-data?metric-path=Overall%20Application%20Performance%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins=1"
    # ECommerce_E2E/metric-data?metric-path=Overall%20Application%20Performance%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins=15
    r = requests.get(url = APPD_PROTOCOL+APPD_CONTROLLER+'/controller/rest/applications/'+str(application['id'])+'/'+metric+APPD_FORMAT.replace('?', '&'),
                     auth=HTTPBasicAuth(APPD_USER, APPD_PASS))
    dataset = r.json()
    tags = []
    tags.append("application.name:"+str(application["name"]))
    tags.append("application.id:"+str(application["id"]))
    return dataset, tags

def post_applications(applications):
    for application in applications():
        if (application['name'] != ''):
            dataset, tags = get_application_average_response_time(application)
            if (DEBUG): print (dataset)
            if not (len(dataset) > 0):
                continue
            if (dataset[0]['metricName'] != 'METRIC DATA NOT FOUND'):
                metric = stringcase.snakecase(dataset[0]['metricPath'].replace("|","")).replace("__","_")
                for result in dataset[0]['metricValues'][0]:
                    if result in {'value', 'min', 'max', 'sum', 'count', 'standardDeviation'}:
                        response = api.Metric.send(metric="appdynamics."+metric+"."+result, points=dataset[0]['metricValues'][0][result], tags=tags)
                        if (DEBUG): print (response)
    
def main(): 
    post_applications(get_applications)
            
main()