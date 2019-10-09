#!/usr/bin/env python3

import argparse
import os
import re
import xml.etree.ElementTree as ET
import zipfile

# SCP
from paramiko.config import SSH_PORT
from paramiko import SSHClient
from scp import SCPClient


def build_extension(ext_directory) -> (str, str):
    """Packages an extension and updates its file for the update server.

    Args:
        ext_directory (str): path to the root directory of the extension's source code
    
    Returns:
        (str, str): tuple of paths to the freshly created extension package and the modified update file
    """
    # load extension name and slug from directory path
    path = os.path.abspath(ext_directory)
    name = os.path.basename(path)
    slug = name.split('_')[-1]

    # load version from manifest
    manifest_path = os.path.join(path, '{}.xml'.format(slug))
    version = extract_version(manifest_path)

    # remove previous packages
    for f in os.listdir(path):
        if f.startswith(name) and f.endswith('.zip'):
            os.remove(os.path.join(path, f))

    # build new package
    package_file = os.path.join(path, '{}-{}.zip'.format(name, version))
    build_package(path, package_file)

    # update update file
    update_file = os.path.join(path, 'updates', 'extension.xml')
    update_update_file(path, update_file, version, package_file)

    return package_file, update_file

def extract_version(manifest_path) -> str:
    """Extracts the version from an extension manifest file.

    Args:
        manifest_path (str): path to the extension's manifest file

    Returns:
        str: extracted version number string
    """
    xml = ET.parse(manifest_path)
    root = xml.getroot()
    return root.find('version').text  

def build_package(ext_path, package_path):
    """Builds the package of an extension.

    Args:
        ext_path (str): path to the extension directory
        package_path (str): destination path of the new package file
    """
    zip_folder(ext_path, package_path, excludes=[
        # exclude build scripts
        '/mkzip.py',
        '/mkzip.sh',
        # exclude updates folder
        '/updates/',
        # exclude hidden files and directories
        '/\..*',
        '/\..*/',
        # exclude currently building package file
        '/' + os.path.basename(package_path),
    ])

def update_update_file(ext_path, update_path, version, package_path):
    """Replaces the update entry in the update server file of an extension with the specified release.

    Args:
        ext_path (str): path to the extension directory
        update_path (str): path to the update server file
        version (str): version of the release that is to be published
        package_path (str): path to the extension package of the specified version
    """
    xml = ET.parse(update_path)
    root = xml.getroot()
    # get first update node
    node = root.find('update')
    # update version
    node.find('version').text = version
    # get first url of first downloads node
    url_node = node.find('downloads').find('downloadurl')
    # replace filename in url with new package file name
    url_node.text = '/'.join(url_node.text.split('/')[:-1]) + '/' + os.path.basename(package_path)
    # write new update file
    xml.write(update_path)

def push_extension(ssh_config, remote_dir, package_file, update_file):
    """Pushes the release files of an extension to its update server.

    Args:
        ssh_config (dict): SSH configuration (host, [port], [user], [password])
        remote_dir (str): path to the remote root directory for Joomla! extension update files
        package_file (str): path to the extension package file for the release
        update_file (str): path to the extension update file for the release
    """
    # open SSH client using the provided credentials
    ssh = SSHClient()
    #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    use_password_auth = 'user' in ssh_config or 'password' in ssh_config
    ssh_port = ssh_config['port'] if 'port' in ssh_config else SSH_PORT
    ssh.load_system_host_keys()
    if use_password_auth:
        ssh.connect(ssh_config['host'], ssh_port, ssh_config['user'], ssh_config['password'])
    else:
        ssh.connect(ssh_config['host'])

    # ensure target directory is existing
    remote_target = os.path.join(remote_dir, os.path.basename(os.path.dirname(package_file)))
    ssh.exec_command('mkdir -p {}'.format(remote_target))
    # TODO transfer blank index.html too?
    
    # transfer extension files via SCP
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(update_file, os.path.join(remote_target, os.path.basename(update_file)))
        scp.put(package_file, os.path.join(remote_target, os.path.basename(package_file)))


def zip_folder(folder, target, excludes=None):
    """Zips a folder and its content recursively.

    Args:
        folder (str): path to the folder that is to be zipped
        target (str): destination path of the created zip file
        excludes (list): list of paths that are to be excluded from the zip file (default: None)
    """
    re_excludes = zip_expand_excludes(excludes)
    zipobj = zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(folder) + 1
    for base, dirs, files in os.walk(folder):
        for f in files:
            fn = os.path.join(base, f)
            path = fn[rootlen - 1:]
            if all(re.match(e, path) is None for e in re_excludes):
                zipobj.write(fn, fn[rootlen:])

def zip_expand_excludes(excludes) -> [str]:
    """Transforms the paths for excluding files in a created zip file into regular expressions.

    Args:
        excludes (list): list of paths that are to be excluded when creating the zip file
    
    Returns:
        list: list of regular expressions to match paths that are to be excluded
    """
    # target format '^[(.*/)]whatsoever[/.*]$' where part wrapped in [] are dependent on the entry
    return [
        '^{prefix}{path}{suffix}$'.format(
            prefix='(.*/)' if not e.startswith('/') else '',
            path=e,
            suffix='/.*' if e.endswith('/') else ''
        ) for e in excludes]


def process_args(args):
    """Processes parsed command line arguments to build and push an extension release.

    Args:
        args (argparse.Namespace): parsed command line arguments
    """
    # build the specified extension
    package_file, update_file = build_extension(args.path)
    # push the extension files to its update server, if desired
    if args.push:
        # build SSH config object
        ssh_config = {
            'host': args.ssh_host,
        }
        if args.ssh_port:
            ssh_config['port'] = args.ssh_port
        if args.ssh_user:
            ssh_config['user'] = args.ssh_user
        if args.ssh_password:
            ssh_config['password'] = args.ssh_user
        # use SCP to push the extension files
        push_extension(ssh_config, args.remote_dir, package_file, update_file)

if __name__ == "__main__":
    # build argument parser
    parser = argparse.ArgumentParser(description='Create and publish packages of Joomla! extensions.')
    parser.add_argument('--push', action='store_const', const=True, help='push the extension package to the specified update server')
    parser.add_argument('-s', '--ssh_host', help='specify the SSH host, if pushing an update')
    parser.add_argument('-P', '--ssh_port', help='specify the SSH port, if pushing an update')
    parser.add_argument('-u', '--ssh_user', help='specify the SSH user, if pushing an update')
    parser.add_argument('-p', '--ssh_password', help='specify the SSH password, if pushing an update')
    parser.add_argument('-d', '--remote_dir', help='remote directory of the extension')
    parser.add_argument('path', help='path to the extension directory')
    # parse passed arguments
    args = parser.parse_args()
    # validate (combination of) arguments
    if args.push and not (args.ssh_host and args.remote_dir):
        parser.error('The SSH host and the remote directory have to be specified when pushing an extension to its update server!')
    # process arguments
    process_args(args)
