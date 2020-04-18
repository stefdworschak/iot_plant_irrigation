import json

from django.shortcuts import render, redirect

from .aws_iot import (list_things, create_thing, create_credentials,
                      attach_policy)

# Create your views here.
def index(request):
    return render(request, 'index.html')


def add_thing(request):
    thing_name = request.POST.get('thing_name')
    new_thing = create_thing(thing_name)
    things_list = json.loads(list_things())
    return render(request, 'output.html', {'json_response': things_list, 
                                           'thing_name': thing_name})


def add_credentials(request):
    thing_name = ''
    POLICY_NAME = 'AWSIOTPolicy'
    new_credentials = json.loads(create_credentials())
    attached_policy = attach_policy(POLICY_NAME, 
                                 new_credentials.get('certificateArn'))
    response = {
        'credentials': new_credentials,
        'attached_policy': attached_policy,
    }
    return render(request, 'output.html', {'json_response': response, 
                                           'thing_name': thing_name})
