from __future__ import with_statement
from fabric.api import *
from fabric.contrib.files import exists
from contextlib import contextmanager as _contextmanager
import re, os, json

##############
### config ###
##############
local_dir = os.getcwd()
app_git_repo = re.search("git@github.com:.+(.git)",open('./.git/config').read()).group(0)
app_name = app_git_repo.split('/')[1][:-4]  

local_config_dir = os.path.dirname(os.path.realpath(__file__)) +'/config'
remote_deploy_dir = '/home/deploy'
nginx_sites_availables = '/etc/nginx/sites-available'
nginx_sites_enabled = '/etc/nginx/sites-enabled'
remote_supervisor_dir = '/etc/supervisor/conf.d'

env.hosts = ['dev.100mdeep.com']  # default host name, override in command line if you'd like. flops create:hosts="100mdeep.com"
env.user = 'deploy'
env.password = os.environ.get('REMOTE_SUDO_PWD')
system_package_to_install = ["python", "python-pip", "python-virtualenv", "nginx", "supervisor", "git"]

# env.keyfile = ['$HOME/.ssh/deploy_rsa']
env.directory = '~'
env.activate = 'source ~/.'+app_name+'/bin/activate'

@_contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield

#############
### tasks ###
#############
sudo_apt_install = lambda x: sudo('apt-get install -y '+x)

def checks():
    if (env.password == None): abort("Please set env variable REMOTE_SUDO_PWD")


def install_requirements():
    """ Install required packages. """
    sudo('apt-get update')
    map(sudo_apt_install, system_package_to_install)


def install_flask_app():
    """
    1. Create and activate a virtualenv
    2. Clone Flask project to remote host
    """
    with cd(remote_deploy_dir):
        run('git clone '+ app_git_repo)
        run('virtualenv .'+app_name)
        with virtualenv():
            run('pip install flask gunicorn')
            run('pip install -r '+app_name+'/requirements.txt')


def nginx_enable(app_name):
    #will need to customize the template here.
    nginx_config_file = local_config_dir+'/nginx_flask_deploy'
    if exists(nginx_sites_enabled+'/default'):
        sudo('rm '+nginx_sites_enabled+'/default')
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
    if exists(remote_supervisor_dir+'/'+app_name+".conf") is False:
        with cd(remote_supervisor_dir):
            put(local_config_dir+'/flask_project.conf', './'+app_name+".conf", use_sudo=True)
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


def status():
    """ Is our app live? """
    sudo('supervisorctl status')


def create():
    local('pipreqs . --force')
    install_requirements()
    install_flask_app()
    nginx_enable(app_name)
    configure_supervisor(app_name)
    # configure_git()


def delete():
    sudo('rm -rf ~/'+app_name+' ~/.'+'~/'+app_name)   
    if exists(nginx_sites_availables+'/'+app_name) is True:
        sudo('rm '+nginx_sites_availables+'/'+app_name)
    if exists(nginx_sites_enabled+'/'+app_name) is True:
        sudo('rm '+nginx_sites_enabled+'/'+app_name)
    if exists(remote_supervisor_dir+'/'+app_name+".conf") is True:
        sudo('sudo supervisorctl stop '+app_name)
        sudo('rm '+remote_supervisor_dir+'/'+app_name+".conf")
    sudo('service nginx restart')

#usage
#WANT TO BE ABLE TO CALL: fab flops dev.100mdeep.com:80 and have the current git reop deployed there.
