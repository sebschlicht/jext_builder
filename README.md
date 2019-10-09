# Joomla! Extension Builder

The script in this repository allows to package a Joomla! extension and optionally push this new release to an update server.

## Usage

The following is the output of the script's help:

    $ ./build-jext -h
    usage: build-jext.py [-h] [--release] [-s SSH_HOST] [-P SSH_PORT]
                        [-u SSH_USER] [-p SSH_PASSWORD] [-d REMOTE_DIR]
                        path

    Build and release packages of Joomla! extensions.

    positional arguments:
    path                  path to the extension directory

    optional arguments:
    -h, --help            show this help message and exit
    --release             push the extension package to the specified update
                            server
    -s SSH_HOST, --ssh_host SSH_HOST
                            specify the SSH host for pushing the update (required
                            if releasing)
    -P SSH_PORT, --ssh_port SSH_PORT
                            specify the SSH port for pushing the update (optional)
    -u SSH_USER, --ssh_user SSH_USER
                            specify the SSH user for pushing the release (if not
                            using a SSH key)
    -p SSH_PASSWORD, --ssh_password SSH_PASSWORD
                            specify the SSH password for publishing the release
                            (see ssh_user)
    -d REMOTE_DIR, --remote_dir REMOTE_DIR
                            remote root directory for Joomla extensions (required
                            if relasing)
