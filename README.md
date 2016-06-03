# Flops
Flask Ops: production quality deployment for Flask Apps.

1. Create 'deploy' on the server with sudo rights.
2. Create a flask app, named app.py and push it to github.
3. Execute pip install pipreqs (in case you don't have it installed).
5. Make sure that you're are pulling from github using SSH (i.e. that the github remote address is of the following form: git@github.com:migloo/test-app.git)
6. Create an alias by adding the following command to your bash profile file: alias flops='fab -f /path/to/this/repository/fabfile.py'
7. To use: from any directory that has flask app.py file, execute 'flops create' or 'flops delete', or flops create:hosts='your_host_name'
