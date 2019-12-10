# Joomla! Extension Builder

The script in this repository allows to package a Joomla! extension and optionally push this new release to an update server.

## Example

For an extension `com_nuliga` the following builder call

    /path/to/build-jext.py /path/to/com_nuliga

1. removes all previous package files in the extension's folder,
1. creates a new package file, such as `com_nuliga-0.2.0.zip` and
1. updates the extension's update file (i.e. `updates/extension.xml`) to current new version number and package file name

If the script is also releasing the package, both the created package file and the modified update file are pushed to the update server of the extension afterwards.
The SSH connection details to this server can be specified using various command line arguments (see [usage section](#usage)):

    /path/to/build-jext.py /path/to/com_nuliga --release -s domain.com

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
