
#change here the paths, they are outdated.
sudo apt-get update
sudo apt-get install -y python python-pip python-virtualenv nginx supervisor git

cd ~ && git clone https://github.com/migloo/flask_project.git
virtualenv env
source env/bin/activate
pip install flask gunicorn

sudo rm /etc/nginx/sites-enabled/default
sudo cp /home/deploy/flask_project/config/flask_deploy /etc/nginx/sites-available/flask_deploy
sudo ln -s /etc/nginx/sites-available/flask_deploy /etc/nginx/sites-enabled/flask_deploy
sudo cp /home/deploy/flask_project/config/flask_project.conf  /etc/supervisor/conf.d/flask_project.conf

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start flask_project
sudo service nginx restart