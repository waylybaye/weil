import os
from fabric.api import run, local, sudo
from fabric.colors import green, blue, red
from fabric.contrib import files
from fabric.context_managers import cd, prefix, hide


def _success(msg):
    print green(msg)


def _info(msg):
    print blue(msg)


def _error(msg):
    print red(msg)


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

    # Find git origin url

    with cd("~/www"):
        run('git clone %s %s' % (git, name))

    with cd("~/env"):
        run("virtualenv %s" % name)


def _is_package_installed(executable):
    """where a command exists"""
    return run('which ' + executable, quiet=True)


def install_essentials():
    """
    Install essential software:
    supervisor, python-setuptools
    """
    if not _is_package_installed("python-setuptools"):
        with hide('running', 'stdout'):
            print blue("Installing python-setuptools ... "),
            sudo("apt-get install python-setuptools")
            print green("success")
    else:
        print green("Found python-setuptools")

    if not _is_package_installed("supervisorctl"):
        with hide('running', 'stdout'):
            print blue("Installing supervisor ... "),
            sudo('easy_install supervisor')
            print green('success')
    else:
        print green("Found supervisor")

    if not _is_package_installed("git"):
        with hide('running', 'stdout'):
            print blue('Installing git ... '),
            sudo('apt-get install git')
            print green('success')
    else:
        print green("Found git ")


def setup_supervisord(name):
    pass


def start(name):
    sudo("supervisorctl start %s" % name)


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
    app_root = "~/www/%s" % name
    env = "~/env/%s" % name

    with cd(app_root):
        run('git pull')
        with prefix('source %s/bin/activate' % env):
            run('pip install -r requirements.txt')
            run('python manage.py syncdb')
            run('python manage.py migrate')
            run('python manage.py collectstatic --noinput')


def env(name, command=None, **kwargs):
    """
    management app environment variables
    `command`:
        `list`: list all env

    fab env:list
    fab env:DATABASE_URL="" add or change env
    """


def hello():
    if not run('which 23434', quiet=True):
        print "NONO"
    with hide('stdout'):
        result = run('ls')
        print type(result), result, result.endswith('www')


def remote_env(config_file, command=None, **kwargs):
    """
    NOTE: This command is run on remote server, don't call directly
    """
    if command == 'list':
        pass

