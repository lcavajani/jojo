#!/usr/bin/env python3

import argparse
from distutils.util import strtobool
import logging
import os
import platform
import subprocess

import default
from action.new_project_action import NewProjectAction
from action.find_version_action import FindVersionAction
from action.list_version_action import ListVersionAction
from action.build_action import BuildAction
from action.push_action import PushAction


def parse_args():
    parser = argparse.ArgumentParser()

    # Verify that we are being executed with Python 3+
    if int(platform.python_version_tuple()[0]) <= 2:
        parser.error('jojo requires Python 3.x')

    # Parent parser used by all commands
    parent_parser = argparse.ArgumentParser(
        description='jojo is here to take care of container images!',
        add_help=False,
    )
    parent_parser.add_argument(
        '--log-level',
        default=os.environ.get(
            default.EnvVar.LOG_LEVEL.value,
            default.Config.LOG_LEVEL.value),
        choices=('debug', 'info', 'warn', 'fatal'))
    parent_parser.add_argument(
        '-p', '--path',
        default=os.environ.get(
            default.EnvVar.IMAGES_PATH.value,
            None),
        help='Path to the container images directory')
    parent_parser.add_argument(
        '--dry-run',
        default=bool(strtobool(os.environ.get(
            default.EnvVar.DRY_RUN.value,
            default.Config.DRY_RUN.value))),
        action='store_true',
        help='Do not write any files or execute commands')
    parent_parser.add_argument(
        '--builder',
        default=os.environ.get(
            default.EnvVar.BUILDER.value,
            default.Builder.NAME.value),
        choices=['buildah', 'buildkit', 'podman'])

    subparsers = parser.add_subparsers(
        title='commands', description='commands')

    # new command
    new_project = subparsers.add_parser(
        'new', help='Create a new image project',
        parents=[parent_parser])
    new_project.add_argument(
        '--alpine-package',
        default=default.Alpine.PACKAGE.value,
        help='Alpine package to use as version')
    new_project.add_argument(
        '--alpine-repo',
        default=default.Alpine.REPO.value,
        help='Alpine repository to use for the package')
    new_project.add_argument(
        '--alpine-version-id',
        default=default.Alpine.VERSION_ID.value,
        help='Alpine version id of the repository')
    new_project.add_argument(
        '--from-image-builder',
        help='Image to use for the builder')
    new_project.add_argument(
        '--from-image',
        help='Image to use as the base image')
    new_project.add_argument(
        '--github-owner',
        default=default.Github.OWNER.value,
        help='GitHub owner of the repository')
    new_project.add_argument(
        '--github-repo',
        default=default.Github.REPO.value,
        help='GitHub repository to use for the version')
    new_project.add_argument(
        '--image',
        default=default.Image.NAME.value,
        help='Image to build')
    new_project.add_argument(
        '--version-from',
        choices=['alpine', 'github'],
        help='Select the source of the package')
    new_project.add_argument(
        'image', action=NewProjectAction)

    # listver command
    list_version = subparsers.add_parser(
        'listver', help='List the available version of a package',
        parents=[parent_parser])
    list_version.add_argument(
        '--first-versions',
        default=default.Config.FIRST_VERSIONS_LIST.value,
        help='Release versions to query, from new to old')
    list_version.add_argument(
        'image', action=ListVersionAction)

    # findver command
    find_version = subparsers.add_parser(
        'findver', help='Find the latest version of a package',
        parents=[parent_parser])
    find_version.add_argument(
        '--first-versions',
        default=default.Config.FIRST_VERSIONS_FIND.value,
        help='Release versions to query, from new to old')
    find_version.add_argument(
        'image', action=FindVersionAction)

    # build command
    build = subparsers.add_parser(
        'build', help='Build a container image',
        parents=[parent_parser])
    build.add_argument(
        '--addr',
        help='Address to connect to')
    build.add_argument(
        '--push',
        default=False,
        action='store_true',
        help='Push the image after the build')
    build.add_argument(
        '--tag-latest',
        default=default.Config.TAG_LATEST.value,
        action='store_true',
        help='Tag built image as latest')
    build.add_argument(
        'image', action=BuildAction)

    # push command
    push = subparsers.add_parser(
        'push', help='Push a container image',
        parents=[parent_parser])
    push.add_argument(
        '--tag-latest',
        default=default.Config.TAG_LATEST.value,
        action='store_true',
        help='Tag image as latest before pushing')
    push.add_argument(
        'image', action=PushAction)

    parser.parse_args()


def main():
    try:
        parse_args()
    except subprocess.CalledProcessError as error:
        logging.debug('Stack Trace: %s', error)
        logging.error('Unable to execute command: %s', error)
    # TODO: redo this
    raise SystemExit


if __name__ == '__main__':
    main()
