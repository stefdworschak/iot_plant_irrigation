from datetime import datetime
import hashlib
import json
import os
import re
import subprocess
import tempfile

from django.contrib.staticfiles import finders

WATER_PLANT_LAMBDA = 'arn:aws:lambda:eu-west-1:790430310068:function:water_plant'

def create_thing_name(thing_name):
    gen_hash = hashlib.sha256()
    gen_hash.update(str(datetime.now()).encode('utf-8'))
    hex_digest = gen_hash.hexdigest()
    thing_expression = thing_name.lower()[:6]
    return thing_expression + '-' + hex_digest[-6:]


def list_things():
    result = subprocess.check_output(['aws','iot','list-things'])
    return result


def create_thing(thing_name):
    result = subprocess.check_output(['aws','iot','create-thing', '--thing-name',
                                      thing_name])
    return result


def create_credentials():
    result = subprocess.check_output(['aws','iot','create-keys-and-certificate',
                                      '--set-as-active'])
    return result


def open_policy(thing_name):
    filepath = finders.find('policies/original_policy.json')
    with open(filepath) as file:
        raw_policy = file.read()
    policy = raw_policy.replace('%s', thing_name)
    return policy


def create_policy(thing_name):
    policy = open_policy(thing_name)
    result = subprocess.check_output(['aws','iot', 'create-policy', 
                                      '--policy-name', (thing_name + '_policy'),
                                      '--policy-document', policy])
    return result


def attach_policy(policy_name, target):
    try:
        subprocess.check_output(['aws','iot','attach-policy',
                                 '--policy-name', policy_name,
                                 '--target', target])
        return True
    except Exception as e:
        print('An error occurred: %s' % (e))
        return False


def delete_policy(policy_name):
    result = subprocess.check_output(['aws','iot', 'delete-policy', 
                                      '--policy-name', policy_name])
    return result

def deactivate_certificate(certificate_arn):
    certificate_id = certificate_arn.split('/')[1]
    result = subprocess.check_output(['aws','iot', 'update-certificate', 
                                      '--certificate-id', certificate_id,
                                      '--new-status', 'INACTIVE'])
    return result

def delete_certificate(certificate_arn):
    certificate_id = certificate_arn.split('/')[1]
    result = subprocess.check_output(['aws','iot', 'delete-certificate', 
                                      '--certificate-id', certificate_id,
                                      '--force-delete'])
    return result


def delete_iot_thing(thing_name):
    result = subprocess.check_output(['aws','iot', 'delete-thing', 
                                      '--thing-name', thing_name])
    return result

def create_iot_rule(thing_name, rule_action, rule_params, rule_num):
    actions = {
        'water_plant': WATER_PLANT_LAMBDA,
    }
    sql = ("SELECT * FROM '$aws/things/%s/shadow/update/accepted' WHERE state.desired.type = 'publish' AND state.desired.data.%s"
            % (thing_name, rule_params))

    description = "%s for %s, num: %s" % (rule_action, thing_name, rule_num)
    print(sql)
    payload = json.dumps({
        "sql": sql,
        "description": description,
        "actions": [
            {
                "lambda": {
                    "functionArn": actions[rule_action]
                }
            }
        ]
    })
    rule_name = re.sub('[-:]','_',thing_name) + "_" + rule_num
    result = subprocess.check_output(['aws','iot', 'create-topic-rule', 
                                      '--rule-name', rule_name,
                                      '--topic-rule-payload', payload])
    return result