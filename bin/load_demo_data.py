#!/usr/bin/env python
# Copyright (c) Swissto12 SA 2025 All rights reserved.
import argparse
import json
import logging
import sys
from os import getenv
from typing import Optional

import dotenv
import requests

"""
    Loads a TAS file into a new program/flight model
"""
# arg parser will re-assign
program_name = ''
customer_name = ''
spacecraft_name = ''
tas_file_name = ''

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

dotenv.load_dotenv('.env')

host = getenv('FLASK_HOST', 'localhost')
port = getenv('FLASK_PORT', '5000')
client_id = getenv('CLIENT_ID', 'nestservice')
client_secret = getenv('CLIENT_SECRET', 'nestservicesecret')
oidc_endpoints = getenv('OIDC_ENDPOINTS', 'http://localhost:3008/realms/local-development').split(',')

url = f'http://{host}:{port}'


# get a token
def get_token():
    for oidc_endpoint in oidc_endpoints:
        doc = requests.get(f'{oidc_endpoint}/.well-known/openid-configuration', headers={'accept': 'application/json'}).json()
        token_url = doc.get('token_endpoint')
        token_payload = requests.post(
            token_url,
            f'grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            auth=(client_id, client_secret),
        ).json()
        token = token_payload.get('access_token')
        return token
    return ''


def request(method='GET', path='', payload: Optional[dict] = None, content_type='application/json', accept='application/json'):
    token = get_token()
    headers = {'accept': accept, 'Authorization': f'Bearer {token}', 'content-type': content_type}
    body = payload
    if payload and 'json' in content_type:
        body = json.dumps(payload)
    result = requests.request(method=method, url=f'{url}{path}', data=body, headers=headers)
    logger.info(f'{result.status_code} {result.text}')
    return result


def run():
    logger.info(f'Checking for program {program_name}')
    result = request('GET', f'/programs/{program_name}')
    if result.status_code == 404:
        logger.info(f'Creating program {program_name}...')
        result = request('POST', '/programs', {'reasonForChange': 'load test data', 'programs': [{'name': program_name, 'customer': customer_name}]})
        logger.info(f'{result.status_code} {result.text}')
        if result.status_code != 201:
            return
    else:
        logger.info(f'Checking for program {program_name}')

    zipped_file_data: bytes = open(tas_file_name, 'rb').read()
    logger.info('Loading TAS import...')
    request('PUT', f'/imports/tas/ids/{program_name}', payload=zipped_file_data, content_type='application/octet-stream')

    logger.info(f'Checking for flight model {spacecraft_name}')
    result = request('GET', f'/flight-models/{spacecraft_name}')
    if result.status_code == 404:
        logger.info(f'Creating flight model {spacecraft_name}...')
        request('POST', '/flight-models', {'reasonForChange': 'load test data', 'flightModels': [{'program': program_name, 'name': spacecraft_name}]})
    # TODO: load some other test data for UI:
    result = request(
        'POST',
        '/curves',
        {
            'reasonForChange': 'loading test data',
            'curves': [
                {
                    'curveName': 'TEST_POLY',
                    'radix': 'D',
                    'description': 'The poly test',
                    'engType': 'I',
                    'rawType': 'I',
                    'units': '1',
                    'polyCurve': {'coeff0': '1', 'coeff1': '2', 'coeff2': '3', 'coeff3': '4', 'coeff4': '5'},
                },
                {'curveName': 'TEST_NUMERIC', 'radix': 'O', 'engType': 'I', 'rawType': 'I', 'numCurve': {'xvals': [1, 2], 'yvals': [3, 4]}},
                {'curveName': 'TEST_LOG', 'radix': 'D', 'logCurve': {'coeff0': '5', 'coeff1': '4', 'coeff2': '3', 'coeff3': '2', 'coeff4': '1'}},
                {'curveName': 'TEST_TEXT', 'textCurve': [
                    {'low': 0,'high': 3,'textValue': 'LOW'},
                    {'low': 4, 'high': 9, 'textValue': 'MID'},
                    {'low': 10, 'high': 1000000, 'textValue': 'HIGH'}
                ]},
            ],
        },
    )
    result = request(
        'POST',
        '/monitors',
        {
            "monitors":[
                {"monitorName":"TEST_HS_01","description":"PMON_1","program":"HummingSat","isEnabled":True,
                 "interpretation":"U","numFails":1,"validityParameters":[],
                 "parameter":{"parameterName":"AO_30.AJ_ANGLE_BIAS_REMOVAL_RATE",
                              "absoluteName":"","apid":30,"monitoringInterval":0,
                              "maxReportingDelay":0,"isPMON":True,
                              "isParameterGroundMon":False,
                              "checks":[
                              {"limit":{"flightModel":"HS01","type":"int","limitCheckType":None,
                                        "yellowHigh":None,"yellowLow":None,"redHigh":None,"redLow":1,
                                        "lowEventName":"AO_30.ATM_AO_APPLICATION_INACTIVE",
                                        "lowCustomEventId":None,"highCustomEventId":None}}
                              ]}},
                {"monitorName":"TEST_HS_02","description":"PMON_1","program":"HummingSat","isEnabled":True,
                 "interpretation":"U","numFails":1,"validityParameters":[],
                 "parameter":{"parameterName":"AO_30.AJ_ANGLE_BIAS_REMOVAL_RATE",
                              "absoluteName":"","apid":30,"monitoringInterval":0,
                              "maxReportingDelay":0,"isPMON":True,
                              "isParameterGroundMon":False,
                              "checks":[
                              {"limit":{"flightModel":"HS01","type":"int","limitCheckType":None,
                                        "yellowHigh":None,"yellowLow":None,"redHigh":None,"redLow":1,
                                        "lowEventName":"AO_30.ATM_AO_APPLICATION_INACTIVE",
                                        "lowCustomEventId":None,"highCustomEventId":None}}
                              ]}},
                {"monitorName":"TEST_HS_03","description":"PMON_1","program":"HummingSat","isEnabled":True,
                 "interpretation":"U","numFails":1,"validityParameters":[],
                 "parameter":{"parameterName":"AO_30.AJ_ANGLE_BIAS_REMOVAL_RATE",
                              "absoluteName":"","apid":30,"monitoringInterval":0,
                              "maxReportingDelay":0,"isPMON":True,
                              "isParameterGroundMon":False,
                              "checks":[
                              {"limit":{"flightModel":"HS01","type":"int","limitCheckType":None,
                                        "yellowHigh":None,"yellowLow":None,"redHigh":None,"redLow":1,
                                        "lowEventName":"AO_30.ATM_AO_APPLICATION_INACTIVE",
                                        "lowCustomEventId":None,"highCustomEventId":None}}
                              ]}},
                {"monitorName":"TEST_HS_04","description":"PMON_1","program":"HummingSat","isEnabled":True,
                 "interpretation":"U","numFails":1,"validityParameters":[],
                 "parameter":{"parameterName":"AO_30.AJ_ANGLE_BIAS_REMOVAL_RATE",
                              "absoluteName":"","apid":30,"monitoringInterval":0,
                              "maxReportingDelay":0,"isPMON":True,
                              "isParameterGroundMon":False,
                              "checks":[
                              {"limit":{"flightModel":"HS01","type":"int","limitCheckType":None,
                                        "yellowHigh":None,"yellowLow":None,"redHigh":None,"redLow":1,
                                        "lowEventName":"AO_30.ATM_AO_APPLICATION_INACTIVE",
                                        "lowCustomEventId":None,"highCustomEventId":None}}
                              ]}}
            ],
            "reasonForChange":"test"}
    )
    result = request(
        'POST',
        '/report-definitions',
        {
            'reasonForChange': 'loading test data',
            'reportDefinitions': [
                {
                    'name': 'TEST_HK',
                    'description': 'TEST DATA ',
                    'program': 'HummingSat',
                    'sid': 99999,
                    'numRepetitions': 1,
                    'defaultEnabled': False,
                    'isProtected': False,
                    'isHousekeeping': True,
                    'conditionParamName': 'AJ_SF_ANODE_VOLTAGE_DELTA_VCRP_CHECK.EQ_PPU_38',
                    'parameterNames': [
                        'AJ_SF_ANODE_VOLTAGE_DELTA_VCRP_CHECK.EQ_PPU_38',
                        'AJ_SF_ANODE_VOLT_RAMP_DOWN_INC.EQ_PPU_38',
                        'AJ_SF_ANODE_VOLT_RAMP_UP_INC.EQ_PPU_38',
                        'AJ_SF_CRP_VOLT_PROT_THR_HIGH.EQ_PPU_38',
                        'AJ_SF_CRP_VOLT_PROT_THR_LOW.EQ_PPU_38',
                        'AJ_SF_DISCHARGE_VOLT_PROT_THR.EQ_PPU_38',
                        'AJ_SF_EPR_XFC_IV_LOW_VOLT_EPR_APS.EQ_ACE_16',
                        'AJ_SF_EPR_XFC_IV_LOW_VOLT_EPR_HET.EQ_ACE_16',
                        'AJ_SF_EPR_XFC_IV_LOW_VOLT.EQ_ACE_16',
                        'AJ_SF_HEATER_VOLTAGE_PROT_THR.EQ_PPU_38',
                        'AJ_SF_MAGNET_VOLTAGE_PROT_HIG.EQ_PPU_38',
                        'AJ_SF_MAGNET_VOLTAGE_PROT_LOW.EQ_PPU_38',
                        'AJ_SF_THERMO_VOLTAGE_PROT_THR.EQ_PPU_38',
                    ],
                    'flightModels': [],
                }
            ],
        },
    )


argparser = argparse.ArgumentParser()
argparser.add_argument('-c', '--customer', type=str, help='Customer Name for program', default='SWISSto12')
argparser.add_argument('-p', '--program', type=str, help='Program Name', default='HummingSat')
argparser.add_argument('-s', '--spacecraft', type=str, help='Spacecraft Name', default='HS01')
argparser.add_argument('-f', '--file', type=str, help='TAS zip file name', default='./tests/tas/xml/IDS_XML_20250919.zip')
argparser.add_argument('--nest-url', type=str, help='Full base URL for the NEST service, e.g. http://nest.local', default=None)
argparser.add_argument(
    '--oidc-endpoint', type=str, help='OIDC endpoint for Keycloak, e.g. http://keycloak.local/realms/local-development', default=None
)
args = argparser.parse_args()

# Allow override of host/port/url/oidc via CLI
if args.nest_url:
    url = args.nest_url.rstrip('/')
else:
    url = f'http://{host}:{port}'

if args.oidc_endpoint:
    oidc_endpoints = [args.oidc_endpoint.rstrip('/')]

program_name = args.program
customer_name = args.customer
spacecraft_name = args.spacecraft
tas_file_name = args.file

if __name__ == '__main__':
    print("""
Usage example for Minikube:

    export CLIENT_ID=nestservice
    export CLIENT_SECRET=nestservicesecret
    python tests/load_demo_data.py --nest-url http://nest.local --oidc-endpoint http://keycloak.local/realms/local-development \
           -c <customer> -p <program> -s <spacecraft> -f <tas_zip>

You can also set CLIENT_ID and CLIENT_SECRET as needed for your Keycloak instance.
""")
    run()
