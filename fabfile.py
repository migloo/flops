from __future__ import with_statement
###############
### imports ###
###############
import re, os, json
from fabric.api import *
from fabric.contrib.files import exists
from contextlib import contextmanager as _contextmanager

##############
### config ###
##############
local_dir = os.path.dirname(os.path.abspath(__file__))
deploy_config_json = local_dir+'\\'+'deploy_params.json'
deploy_param  = json.load(open(deploy_config_json))
app_git_repo = deploy_param['git_repo']
app_name = re.search(".+(?=.git)",app_git_repo.split('/')[-1]).group(0)   

local_config_dir = './config'
remote_deploy_dir = '/home/deploy'
nginx_sites_availables = '/etc/nginx/sites-available'
nginx_sites_enabled = '/etc/nginx/sites-enabled'
remote_supervisor_dir = '/etc/supervisor/conf.d'

env.hosts = [deploy_param['server_ip_or_domain']]  # replace with IP address or hostname
env.user = 'deploy'
env.password = os.environ.get('SERVER_SUDO_PWD')
if (env.password == None): print "ERROR: SUDO PASSWORD NOT SET"

# env.keyfile = ['$HOME/.ssh/deploy_rsa']
env.directory = '~'
env.activate = 'source ~/env/bin/activate'

@_contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield

#############
### tasks ###
#############
def install_requirements():
    """ Install required packages. """
    sudo('apt-get update')
    sudo('apt-get install -y python')
    sudo('apt-get install -y python-pip')
    sudo('apt-get install -y python-virtualenv')
    sudo('apt-get install -y nginx')
    sudo('apt-get install -y supervisor')
    sudo('apt-get install -y git')


def install_flask_app(app_git_repo):
    """
    1. Create and activate a virtualenv
    2. Clone Flask project to remote host
    """
    with cd(remote_deploy_dir):
        run('git clone '+ app_git_repo)
        run('virtualenv env')
        with virtualenv():
            run('pip install flask gunicorn')


def nginx_enable(app_name):
    #will need to customize the template here.
    nginx_config_file = local_config_dir+'/nginx_flask_deploy'
    if exists('/etc/nginx/sites-enabled/default'):
        sudo('rm /etc/nginx/sites-enabled/default')
    put(nginx_config_file, nginx_sites_availables+'/'+app_name, use_sudo=True) 

    with cd(nginx_sites_availables):
        sudo("sed -i -- 's/your_app_name/"+app_name+"/g' "+app_name) 

    if exists(nginx_sites_enabled+'/'+app_name) is False:
        sudo('ln -s '+nginx_sites_availables+'/'+app_name+' '+nginx_sites_enabled+'/'+app_name)
    sudo('/etc/init.d/nginx restart')


def configure_supervisor(app_name):
    """
    1. Create new supervisor config file
    2. Copy local config to remote config
    3. Register new command
    """
    if exists('/etc/supervisor/conf.d/'+app_name+".conf") is False:
        with lcd(local_config_dir):
            with cd(remote_supervisor_dir):
                put('./flask_project.conf', './'+app_name+".conf", use_sudo=True)
                sudo("sed -i -- 's/your_app_name/"+app_name+"/g' "+app_name+".conf")
                sudo('supervisorctl reread')
                sudo('supervisorctl update')
                sudo('supervisorctl restart '+app_name)



# def configure_git():
#     """
#     1. Setup bare Git repo
#     2. Create post-receive hook
#     """
#     if exists(remote_git_dir) is False:
#         sudo('mkdir ' + remote_git_dir)
#         with cd(remote_git_dir):
#             sudo('mkdir flask_project.git')
#             with cd('flask_project.git'):
#                 sudo('git init --bare')
#                 with lcd(local_config_dir):
#                     with cd('hooks'):
#                         put('./post-receive', './', use_sudo=True)
#                         sudo('chmod +x post-receive')


# def run_app():
#     """ Run the app! """
#     with cd(remote_flask_dir):
#         sudo('supervisorctl start flask_project')


# def deploy():
#     """
#     1. Copy new Flask files
#     2. Restart gunicorn via supervisor
#     """
#     with lcd(local_app_dir):
#         local('git add -A')
#         commit_message = prompt("Commit message?")
#         local('git commit -am "{0}"'.format(commit_message))
#         local('git push production master')
#         sudo('supervisorctl restart flask_project')


# def rollback():
#     """
#     1. Quick rollback in case of error
#     2. Restart gunicorn via supervisor
#     """
#     with lcd(local_app_dir):
#         local('git revert master --no-edit')
#         local('git push production master')
#         sudo('supervisorctl restart flask_project')


# def status():
#     """ Is our app live? """
#     sudo('supervisorctl status')


def create():
    # install_requirements()
    # install_flask_app(app_git_repo)
    nginx_enable(app_name)
    configure_supervisor(app_name)
    # configure_git()

#need to create a list 
#need to install the list of packages 

#usage
#floy create  // without argument must create a dummy app 
#floy create myapp // must create an app according to myapp.json
#see how to produce a 'requirements.txt' file. 
#need a remove app