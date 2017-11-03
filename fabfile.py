from fabric.api import env, run


##### SETTINGS #####

env.project_name = 'DocPub'
env_name = 'docpub'
python_exec = '/home/ubuntu/Envs/docpub/bin/python3'
project_dir = '/home/ubuntu/docpub/docpub'
requirements_location = '/home/ubuntu/docpub/docpub/requirements.txt'
repo = 'origin'
branch = 'master' 

##### FUNCTIONS #####

def prod():


def test():

@print_status('running tests locally')
def run_tests():
    test_command = python_exec + ' manage.py test'

@print_status('pulling git repository')
def pull_repository():
    command = 'git pull {} {}'.format(repo, branch)
    run(command)

