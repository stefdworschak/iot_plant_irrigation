import subprocess

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

def attach_policy(policy_name, target):
    try:
        subprocess.check_output(['aws','iot','attach-policy',
                                 '--policy-name', policy_name,
                                 '--target', target])
        return True
    except Exception as e:
        print('An error occurred: %s' % (e))
        return False