from datetime import datetime
import hashlib
import json

from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.forms.models import model_to_dict
from django.contrib import messages

from things.models import Thing, ThingRule

from .aws_iot import (list_things, create_thing, create_credentials,
                      create_policy, attach_policy, create_thing_name,
                      delete_policy, delete_certificate, deactivate_certificate,
                      delete_iot_thing, create_iot_rule)

from .helper import add_to_zip, delete_from_s3

@login_required(redirect_field_name=None, login_url='/')
def things(request):
    things = Thing.objects.filter(user=request.user).all()
    rules_set = {}
    for thing in things:
        rules_set.setdefault(thing.thing_name, [])
        for rule in thing.rules.all().values():
            rules_set[thing.thing_name].append(rule)
    print(rules_set)
    return render(request, 'things.html', {'things': things.values(), 'rules': rules_set})


@login_required(redirect_field_name=None, login_url='/')
def add_thing(request):
    things = Thing.objects.all().filter(user=request.user)
    if things.count() > 4:
        messages.error(request, 'You already have four things, please delete or updgrade your account.')
        return redirect(reverse('things_index'))

    display_name = request.POST.get('display_name')
    if not display_name:
        return redirect(reverse('things_index'))
    #try:
    thing_name = create_thing_name(display_name)
    thing = json.loads(create_thing(thing_name))
    policy = json.loads(create_policy(thing_name))
    credentials = json.loads(create_credentials())
    #credentials = {'certificatePem':'', 'keyPair': {'PrivateKey': ''}}
    zip_file_url = add_to_zip(credentials, thing_name, request.user.username)
    attached_policy = attach_policy(policy.get('policyName'), 
                                    credentials.get('certificateArn'))
    thing = Thing.objects.create(
        display_name=display_name,
        thing_name=thing_name,
        user=request.user,
        policy_name=policy.get('policyName'),
        certificate_arn=credentials.get('certificateArn'),
        credentials_url=zip_file_url
    )
    return redirect(reverse('things_index'))


@login_required(redirect_field_name=None, login_url='/')
def delete_thing(request):
    print(request.POST.get('thing_id'))
    thing = Thing.objects.get(thing_name=request.POST.get('thing_id'))
    print(1)
    deactivated_certificate = deactivate_certificate(thing.certificate_arn)
    print(2.1)
    deleted_certificate = delete_certificate(thing.certificate_arn)
    print(2.2)
    deleted_policy = delete_policy(thing.policy_name)
    print(3)
    deleted_thing = delete_iot_thing(thing.thing_name)
    print(4)
    deleted_s3_file = delete_from_s3(thing.thing_name)
    print(5)
    thing.delete()
    messages.success(request, 'Thing deleted successfully.')
    return redirect(reverse('things_index'))


@login_required(redirect_field_name=None, login_url='/')
def add_topic_rule(request):
    context = ""
    thing_name = request.POST.get('thing_id')
    print(thing_name)
    rule_action = request.POST.get('rule_action')
    measure = request.POST.get('rule_measure')
    operator = request.POST.get('rule_operator')
    val = request.POST.get('rule_value')
    rule_params = "%s %s %s" % (measure, operator, val)
    thing = Thing.objects.get(thing_name=request.POST.get('thing_id'))
    rules = thing.rules.all()
    rule_num = rules.count()
    if rule_num < 3:
        topic_rule = create_iot_rule(thing_name, rule_action, rule_params, str(rule_num))   
        rule = ThingRule.objects.create(thing=thing, rule=rule_params, action=rule_action)
        thing.rules.add(rule) 
    else:
        messages.error(request, "You alreay have 3 topic rules. Please upgrade your subscription or delete some of your rules to add a new rule.")

    return redirect(reverse('things_index'))