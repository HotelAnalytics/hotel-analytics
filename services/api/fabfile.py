from fabric import api as fab
from datetime import datetime
import sys
import os

images = {
    'hotel-analytics-api': {
        'tag': 'docker.hotel-analytics.com/hotel-analytics-api',
        'file': 'Dockerfile'
    }
}

containers = {
    'hotel-analytics-api': {
        'order': 1,
        'main': True,
        'run': 'python run.py',
        'network': 'hotel-analytics-network',
        'parameters': [
            ('-v', '/app'),
            ('-p', '8080:8000')
        ]
    }
}

networks = {
    'hotel-analytics-network': {
        'parameters': [
            ('--driver', 'bridge')
        ]
    }
}


@fab.task
def build():
    # Build the containers
    with fab.settings(warn_only=True):
        for key, settings in images.items():
            if 'file' in settings:
                fab.local('docker build -t {} -f {} .'.format(settings['tag'], settings['file']))
            else:
                fab.local('docker pull {}'.format(settings['tag']))

def getLocalPath():
    if (sys.platform == 'win32'):
        local = "//"
        path = os.path.dirname(os.path.abspath(__file__)).split("\\")
        for val in path:
            local += val.replace(":", "").lower() + '/'
        return local[:-1]
    else:
        return '`pwd`'


def startContainers(dev=False, image_name=None, env=[('NODE_ENV', 'local')]):
    for key, settings in sorted(containers.items(), key=lambda x: x[1]['order']):
        if image_name is None or image_name == key:
            with fab.settings(warn_only=True):
                # Kill container if it is running
                if fab.local('docker ps | grep {}'.format(key), capture=True):
                    fab.local('docker kill {}'.format(key))
                # Remove the container if it is present
                if fab.local('docker ps -a | grep {}'.format(key), capture=True):
                    fab.local('docker rm -f {}'.format(key))

            # Build the parameters
            parameters = ''
            if ('parameters' in settings):
                for pair in settings['parameters']:
                    if (pair[0] == '-v'):
                        local = getLocalPath()
                        path = '{}:{}'.format(local, pair[1])
                        parameters += ' {} {}'.format(pair[0], path)
                    else:
                        parameters += ' {} {}'.format(pair[0], pair[1])

            # Add environment variables to parameters
            parameters += ''.join([' -e {}={}'.format(x[0], x[1]) for x in env])

            # Add persistent data volumes to parameters
            if 'data_volume' in settings:
                # Make sure we have a data folder for this container if necessary
                fab.local('mkdir -p data/{}'.format(key))

                parameters += ' -v `pwd`/data/{}:{}'.format(key, settings['data_volume'])

            # Set the network
            if 'network' in settings:
                parameters += ' --network={}'.format(settings['network'])

            # Determine the run command
            run_cmd = ''
            if dev and 'run' in settings:
                run_cmd = ' bash'
            elif 'run' in settings:
                run_cmd = ' ' + settings['run']

            # Bring it all together
            cmd = 'docker run {} --name {}{} {}{}'.format(
                '-it' if dev and 'main' in settings and settings['main'] else '-d',
                key,
                parameters,
                images[settings['image']]['tag'] if 'image' in settings else images[key]['tag'],
                run_cmd
            )

            # Run the docker command locally
            fab.local(cmd)


@fab.task
def network():
    for key, settings in networks.items():
        with fab.settings(warn_only=True):
            # Only create the network if it isn't already there
            if not fab.local('docker network ls | grep {}'.format(key), capture=True):
                # Build the parameters
                parameters = ''.join([' {} {}'.format(x[0], x[1]) for x in settings['parameters']]) if 'parameters' in settings else ''

                fab.local('docker network create{} {}'.format(parameters, key))


@fab.task
def up():
    build()
    startContainers()


@fab.task
def dev(build_images=False, name=None):
    if build_images:
        build()
    network()
    startContainers(dev=True, image_name=name)


@fab.task
def db_revision(msg=None):
    fab.local('alembic revision -m "{}" --autogenerate'.format(msg or 'new revision - {}'.format(datetime.utcnow())))


@fab.task
def db_migrate(rel=None, downgrade=None):
    if not downgrade:
        fab.local('alembic upgrade {}'.format(rel or 'head'))
    else:
        fab.local('alembic downgrade {}'.format(rel or '-1'))

    fab.local('alembic history --verbose -r-2:current')
