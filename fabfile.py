from ConfigParser import ConfigParser
import os
import tempfile
from fabric.api import run, local, sudo, get, put, env as _env
from fabric.colors import green, blue, red
from fabric.contrib import files
from fabric.context_managers import cd, prefix, hide, lcd
from fabric.contrib.console import confirm
from fabric.utils import fastprint


def _success(msg=""):
    print green(msg or "success")


def _info(msg, new_line=False):
    if new_line:
        print blue(msg)
    fastprint(blue(msg))


def _error(msg):
    print red(msg)


def _app_paths(name):
    return "/home/%s/www/%s" % (_env.user, name), "/home/%s/env/%s" % (_env.user, name)


def _find_main_dir():
    folders = run('ls -F | grep /')
    for folder in folders.split():
        _path = os.path.join(folder, 'wsgi.py')
        if files.exists(_path):
            return folder.strip('/')


def _mkdir(folders):
    """mkdir if not exists"""
    if not type(folders) in [list, tuple]:
        folders = [folders]

    for folder in folders:
        if not files.exists(folder):
            run('mkdir %s' % folder)


def create_app(name=None, git=None):
    """
    Create an app in remote server
    This will create:
        ~/www/app
        ~/env/app
        ~/run/app.sock
    """

    install_essentials()
    _info("--------- Initialize App ----------")
    _info("creating folders ... ")
    # create ~/www directory if not existing
    project_root = '~/www/%s' % name
    if files.exists(project_root):
        raise Exception("the app is already existed.")

    # create base dirs
    _mkdir(['~/run', '~/env', '~/wwww', '~/log'])

    # change the owner so the gunicorn worker could access it
    run('chown www-data:www-data ~/run')

    with hide('running', 'stdout'):
        with cd("~/www"):
            _info("clone git repo ...  "),
            run('git clone %s %s' % (git, name))
            _success("success")

        with cd("~/env"):
            _info("create virutalenv ... "),
            run("virtualenv %s" % name)
            _success("success")

        with prefix('source ~/env/%s/bin/activate' % name):
            _info("installing gunicorn ... "),
            run('pip install gunicorn')
            _success("success")

    config_supervisor(name)
    start(name)


def _is_package_installed(executable):
    """where a command exists"""
    return run('which ' + executable, quiet=True)


def install_essentials():
    """
    Install essential software:
    supervisor, python-setuptools
    """
    if not _is_package_installed("easy_install"):
        with hide('running', 'stdout'):
            print blue("Installing python-setuptools ... "),
            sudo("apt-get install python-setuptools")
            print green("success")

    if not _is_package_installed("supervisorctl"):
        with hide('running', 'stdout'):
            print blue("Installing supervisor ... "),
            sudo('easy_install supervisor')
            print green('success')

    if not _is_package_installed("virtualenv"):
        with hide('running', 'stdout'):
            _info("Installing virtualenv ... "),
            sudo('easy_install virtualenv')
            _success("success")

    if not _is_package_installed("git"):
        with hide('running', 'stdout'):
            print blue('Installing git ... '),
            sudo('apt-get install git')
            print green('success')


def _download_remote_file(remote_path, local_path="", hide_message=False):
    if not local_path:
        local_path = tempfile.mktemp('.conf')

    if files.exists(remote_path, use_sudo=True):
        if not hide_message:
            _info("Found existed supervisor conf file, downloading ... ")
        with hide('running', 'stdout'):
            get(remote_path, local_path)
        if not hide_message:
            _success()
        return local_path


def config_supervisor(name, **kwargs):
    """
    add supervisor configuration
    """
    _info("Configuring supervisor ... \n")

    temp_path = tempfile.mktemp('.conf')
    parser = ConfigParser()
    conf_path = '/etc/supervisor/conf.d/%s.conf' % name
    project_root = '~/www/%s' % name

    if _download_remote_file(conf_path, temp_path):
        parser.read(temp_path)

    section = 'program:%s' % name
    if not parser.has_section(section):
        parser.add_section(section)

    wsgi_path = ""
    with hide('running', 'stdout'), cd(project_root):
        folders = run('ls -F | grep /')
        for folder in folders.split():
            _path = os.path.join(folder, 'wsgi.py')
            if files.exists(_path):
                wsgi_path = _path.replace('/', '.').strip('.py')
                _info("Found wsgi module: %s \n" % wsgi_path)
                break
        else:
            raise Exception("Can't find wsgi.py when config supervisor and gunicorn")

    command = "/home/%(user)s/env/%(name)s/bin/gunicorn -b unix:/home/%(user)s/run/%(name)s.sock %(wsgi)s:application"\
              % {'user': _env.user, 'name': name, 'wsgi': wsgi_path}

    parser.set(section, 'command', command)
    parser.set(section, 'directory', "/home/%s/www/%s" % (_env.user, name))
    parser.set(section, 'stdout_logfile', "/home/%s/log/%s.log" % (_env.user, name))
    parser.set(section, 'user', 'www-data')
    parser.set(section, 'autostart', 'true')
    parser.set(section, 'autorestart', 'true')
    parser.set(section, 'redirect_stderr', 'true')

    parser.write(open(temp_path, 'w+'))

    _info("Write supervisor config ... \n"),
    put(temp_path, conf_path, use_sudo=True)

    _info("Reloading supervisor ... \n")
    sudo('supervisorctl update')


def config_nginx(name, host):
    """Config nginx to route requests to wsgi process"""
    template = """
upstream %(app)s_server {
    server unix:/home/%(user)s/run/%(app)s.sock fail_timeout=0;
}

server {
    listen 80 default;
    client_max_body_size 4G;
    server_name %(host)s;

    keepalive_timeout 5;

    # path for static files
    # root /path/to/app/current/public;

    location / {
        # checks for static file, if not found proxy to app
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;

        proxy_pass   http://%(app)s_server;
    }

    access_log /var/log/nginx/%(app)s.access.log;
    error_log /var/log/nginx/%(app)s.error.log;
}
    """
    config = template % {
        'user': _env.user,
        'app': name,
        'host': host,
    }
    local_path = tempfile.mktemp('.conf')
    with open(local_path, 'w+') as output:
        output.write(config)

    remote_path = "/etc/nginx/sites-available/%s.conf" % name
    link_path = "/etc/nginx/sites-enabled/%s.conf" % name
    _info("Creating nginx config file under sites-available ... \n")
    put(local_path, remote_path, use_sudo=True)
    _info('Linking nginx config file to sites-enabled ... \n')
    if files.exists(link_path):
        sudo('rm %s' % link_path)
    sudo('ln -s %s %s' % (remote_path, link_path))
    _info("Restarting nginx ... \n")
    sudo('service nginx reload')


def install_requirements(name):
    project_root, env = _app_paths(name)
    if files.exists(os.path.join(project_root, 'requirements.txt')):
        with cd(project_root), prefix('source %s/bin/activate' % env):
            _info("Installing requirements ... \n")
            run('pip install -r requirements.txt')


def delete_app(name=None):
    project_root = '~/www/%s' % name
    if not files.exists(project_root):
        raise Exception("the app is not existing.")

    if confirm('Are you sure to delete this app( all files will be deleted )?', default=False):
        run("rm -rf %s" % project_root)
        run("rm -rf ~/env/%s" % name)


def deploy(name):
    """
    Pull the latest code from remote
    """
    project_root, env = _app_paths(name)
    with cd(project_root):
        run('git pull')

    with cd(project_root), prefix('source %s/bin/activate' % env), hide('running'):
        # initialize the database
        _info("./manage.py syncdb ... \n")
        run('python manage.py syncdb')

        # run south migrations
        _info("./manage.py migrate ... \n")
        run('python manage.py migrate', quiet=True)

        # collect static files
        _info("./manage.py collectstatic --noinput ... \n")
        run('python manage.py collectstatic --noinput')
        start(name)


def _supervisor_status(program):
    with hide('running', 'stdout'):
        text = sudo('supervisorctl status %s' % program)
        return text.split()[1]


def start(name):
    """
    Start the wsgi process
    """
    project_root, env = _app_paths(name)
    if _supervisor_status(name).lower() == 'running':
        _error("The app wsgi process is already started.")
        return

    _info("Starting the app wsgi process ... \n")
    sudo('supervisorctl start %s' % name)

    # check if the wsgi process started
    if _supervisor_status(name).lower() == 'running':
        _success()


def stop(name):
    """Stop the wsgi process"""
    if _supervisor_status(name).lower() != 'running':
        _error("The app wsgi process is not running.")
        return

    _info("Stop the app wsgi process ... \n")
    sudo('supervisorctl stop %s' % name)

    if _supervisor_status(name).lower() == 'stopped':
        _success()


def status(name=""):
    """
    check the process status
    """
    _info("Checking service status ... \n")
    with hide('running', 'stdout'):
        print blue('nginx    :'), sudo('service nginx status')

        text = sudo('supervisorctl status %s' % name)
        gunicorn_status = text.split()[1]
        extra_msg = ""

        if gunicorn_status.lower() == 'running':
            extra_msg = " ".join(text.split()[2:])

        print blue('gunicorn :'), gunicorn_status, extra_msg


def env(name, command=None, **kwargs):
    """
    management app environment variables
    `command`:
        `list`: list all env

    fab env:list
    fab env:DATABASE_URL="" add or change env
    """
    remote_path = '/etc/supervisor/conf.d/%s.conf' % name
    local_path = _download_remote_file(remote_path)
    env = {}
    section = 'program:%s' % name
    if local_path:
        parser = ConfigParser()
        parser.read(local_path)
        if parser.has_option(section, 'environment'):
            environ = parser.get(section, 'environment')
            for entry in environ.split(','):
                key, val = entry.split('=')
                env[key] = val
    else:
        raise Exception("Please run config_supervisor first.")

    if command == 'list':
        if not env:
            print red("There is no environment vars now.")

        for key, val in env.items():
            print key, val

    else:
        for key, val in kwargs.items():
            env[key] = val

        parser.set(section, 'environment', ','.join(["%s='%s'" % (k, v) for k, v in env.items()]))
        parser.write(open(local_path, 'w'))
        _info("Updating environment ... \n")
        put(local_path, remote_path, use_sudo=True)

        _info("Reload supervisor ... \n")
        sudo('supervisorctl update')
        _success()


def hello():
    run("echo Hello")


