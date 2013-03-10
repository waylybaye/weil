from ConfigParser import ConfigParser
import os
from fabric.state import env as _env
import wayly_fabric


def initialize():
    wayly_fabric.create_app(
        name='weil',
        git='git://github.com/waylybaye/weil.git',
    )

    wayly_fabric.supervisor.config(
        name='weil',
        command='gunicorn -b 127.0.0.1:8020 weil.wsgi:application',
        # command="echo $PATH",
        directory="/home/%s/www/weil" % _env.user,
        virtualenv="/home/%s/.virtualenvs/weil" % _env.user,
    )

    wayly_fabric.nginx.config(
        name="weil",
        host='weil.wayly.net',
        proxy='http://127.0.0.1:8020',
        static_dir='/home/%s/www/weil/static' % _env.user,
    )


def remove():
    wayly_fabric.delete_app(
        name='weil',
    )

    wayly_fabric.nginx.delete(
        name='weil',
    )

    wayly_fabric.supervisor.delete(
        name='weil',
    )


def env(command="", **kwargs):
    wayly_fabric.supervisor.env('weil', command, **kwargs)



def start():
    wayly_fabric.supervisor.start('weil')


def stop():
    wayly_fabric.supervisor.stop('weil')


def restart():
    wayly_fabric.supervisor.restart('weil')


def deploy():
    wayly_fabric.deploy('weil')


def log():
    wayly_fabric.supervisor.log('weil')
