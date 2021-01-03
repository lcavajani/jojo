#!/usr/bin/env python3

import argparse
from distutils.util import strtobool
import logging
import os
import platform
import subprocess

import config
from action.new_project_action import NewProjectAction
from action.find_version_action import FindVersionAction
from action.list_version_action import ListVersionAction
from action.build_action import BuildAction


def parse_args():
    # Default to info logging
    parser = argparse.ArgumentParser()

    # Verify that we are being executed with Python 3+
    if int(platform.python_version_tuple()[0]) <= 2:
        parser.error('jojo requires Python 3.x')

    # Parent parser used by all commands
    parent_parser = argparse.ArgumentParser(
        description='jojo is here to take care of container images!',
    )

    subparsers = parser.add_subparsers(
        title='commands', description='commands')

    # Parent parser used by all commands
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        '--log-level',
        default=os.environ.get(
            config.EnvVar.LOG_LEVEL.value,
            config.Defaults.LOG_LEVEL.value),
        choices=('debug', 'info', 'warn', 'fatal'))
    parent_parser.add_argument(
        '-p', '--path',
        default=os.environ.get(
            config.EnvVar.IMAGES_PATH.value,
            None),
        help='Path to the container images directory')
    parent_parser.add_argument(
        "--dry-run",
        default=bool(strtobool(os.environ.get(
            config.EnvVar.DRY_RUN.value,
            config.Defaults.DRY_RUN.value))),
        action="store_true",
        help='Do not write any files or execute commands')
    parent_parser.add_argument(
        '--builder',
        default=os.environ.get(
            config.EnvVar.BUILDER.value,
            config.Defaults.BUILDER.value),
        choices=['buildkit', 'podman'])

    # new command
    new_project = subparsers.add_parser(
        'new', help='Create a new image project',
        parents=[parent_parser])

    new_project.add_argument(
        '--from-image-builder',
        # default='registry/name:tag',
        help='Image to use for the builder')
    new_project.add_argument(
        '--from-image',
        # default='registry/name:tag',
        help='Image to use as the base image')
    new_project.add_argument(
        '--image',
        # required=True,
        default='registry/name:tag',
        help='Image to build')
    new_project.add_argument(
        '--version-from',
        choices=['alpine', 'github'],
        help='Source of the package version')
    new_project.add_argument(
        'image', action=NewProjectAction)

    # listver command
    list_version = subparsers.add_parser(
        'listver', help='List the available version of a package',
        parents=[parent_parser])
    list_version.add_argument(
        'image', action=ListVersionAction)

    # findver command
    find_version = subparsers.add_parser(
        'findver', help='Find the latest version of a package',
        parents=[parent_parser])
    find_version.add_argument(
        'image', action=FindVersionAction)

    # build command
    build = subparsers.add_parser(
        'build', help='Build a container image',
        parents=[parent_parser])
    build.add_argument(
        'image', action=BuildAction)

    parser.parse_args()


def main():
    # parse_args()
    try:
        # parser.parse_args()
        parse_args()
    except subprocess.CalledProcessError as error:
        logging.debug('Stack Trace: %s', error)
        # parser.error('Unable to execute command: {}'.format(error))
    raise SystemExit


if __name__ == "__main__":
    main()
