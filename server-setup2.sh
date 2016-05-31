adduser deploy
sudo adduser deploy sudo

sudo apt-get update
sudo apt-get install -y python python-pip python-virtualenv nginx supervisor

cd /home/deploy
virtualenv env
source env/bin/activate

pip install flask gunicorn
mkdir flask_project && cd flask_project

mkdir static
nano app.py

sudo rm /etc/nginx/sites-enabled/default
sudo mv /etc/nginx/sites-available/nginx_flask_deploy

sudo ln -s /etc/nginx/sites-available/nginx_flask_deploy /etc/nginx/sites-enabled/nginx_flask_deploy
sudo nano /etc/supervisor/conf.d/flask_project.conf

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start flask_project
sudo service nginx restart

