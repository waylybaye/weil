from ConfigParser import ConfigParser
import os
import tempfile
from fabric.api import run, local, sudo, get, put, env as _env
from fabric.colors import green, blue, red
from fabric.contrib import files
from fabric.context_managers import cd, prefix, hide, lcd
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


def create_app(name=None, git=None):
    """
    Create an app in remote server
    This will create:
        ~/www/app
        ~/env/app
        ~/run/app.sock
    """

    install_essentials()

    # create ~/www directory if not existing
    project_root = '~/www/%s' % name
    if files.exists(project_root):
        raise Exception("the app is already existed.")

    if not files.exists('~/run'):
        run('mkdir ~/run')

    if not files.exists('~/env'):
        run('mkdir ~/env')

    if not files.exists('~/log'):
        run('mkdir ~/log')

    # Find git origin url

    with hide('running', 'stdout'):
        with cd("~/www"):
            _info("Clone git repo ...  "),
            run('git clone %s %s' % (git, name))
            _success("success")

        with cd("~/env"):
            _info("Create virutalenv ... "),
            run("virtualenv %s" % name)
            _success("success")

        with prefix('source ~/env/%s/bin/activate' % name):
            _info("Installing gunicorn ... "),
            run('pip install gunicorn')
            _success("success")

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


def config_supervisor(name):
    """
    add supervisor configuration
    """
    temp_path = tempfile.mktemp('.conf')
    parser = ConfigParser()
    conf_path = '/etc/supervisor/conf.d/%s.conf' % name
    project_root = '~/www/%s' % name

    if files.exists(conf_path, use_sudo=True):
        _info("Found existed supervisor conf file, downloading ... ")
        with hide('running', 'stdout'):
            get(conf_path, temp_path)
        _success()
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
                wsgi_path = _path.replace('/', '.')
                _info("Found wsgi module: %s \n" % wsgi_path)
                break
        else:
            raise Exception("Can't find wsgi.py when config supervisor and gunicorn")

    command = "/home/%s/env/%s/bin/gunicorn %s:application" % (_env.user, name, wsgi_path)

    parser.set(section, 'command', command)
    parser.set(section, 'directory', "/home/%s/www/%s" % (_env.user, name))
    parser.set(section, 'process_name', "%s-wsgi" % name)
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

    run("rm -rf %s" % project_root)
    run("rm -rf ~/env/%s" % name)


def pull(name):
    """
    Pull the latest code from remote
    """
    project_root, env = _app_paths(name)
    with cd(project_root):
        run('git pull')
        start(name)


def start(name):
    """
    Start the wsgi process
    """
    project_root, env = _app_paths(name)

    install_requirements(name)

    with cd(project_root), prefix('source %s/bin/activate' % env):
        run('python manage.py syncdb')
        run('python manage.py migrate', quiet=True)
        run('python manage.py collectstatic --noinput')

    config_supervisor(name)


def status(name=""):
    """
    check the process status
    """
    sudo('service nginx status')
    sudo('supervisorctl status')


def env(name, command=None, **kwargs):
    """
    management app environment variables
    `command`:
        `list`: list all env

    fab env:list
    fab env:DATABASE_URL="" add or change env
    """


def hello():
    with hide('running', 'stdout'):
        folders = run('ls -F | grep /')
        print folders, folders.split()
        for folder in folders.split():
            if files.exists(os.path.join(folder, 'wsgi.py')):
                print green(os.path.join(folder, 'wsgi.py'))
                break

    with hide('stdout'):
        result = run('ls')
        print type(result), result, result.endswith('www')


def remote_env(config_file, command=None, **kwargs):
    """
    NOTE: This command is run on remote server, don't call directly
    """
    if command == 'list':
        pass

