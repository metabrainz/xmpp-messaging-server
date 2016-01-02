# comms-server

## Requirements

* ejabberd
* Python 3.5

## Running

### ejabberd

    $ /usr/local/sbin/ejabberdctl --config-dir <absolute path to ejabberd_config directory> [start|live]

### Connection server

    $ /node_modules/.bin/gulp scripts
    $ python manage.py runserver -h localhost
