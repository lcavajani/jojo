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

    subparsers = parser.add_subparsers(
        title='commands', description='commands')

    # new command
    new_project = subparsers.add_parser(
        'new', help='Create a new image project',
        parents=[parent_parser])
    new_project.add_argument(
        '--alpine-package',
        default=config.Defaults.ALPINE_PACKAGE.value,
        help='Alpine package to use as version')
    new_project.add_argument(
        '--alpine-repo',
        default=config.Defaults.ALPINE_REPO.value,
        help='Alpine repository to use for the package')
    new_project.add_argument(
        '--alpine-version-id',
        default=config.Defaults.ALPINE_VERSION_ID.value,
        help='Alpine version id of the repository')
    new_project.add_argument(
        '--from-image-builder',
        help='Image to use for the builder')
    new_project.add_argument(
        '--from-image',
        help='Image to use as the base image')
    new_project.add_argument(
        '--github-owner',
        default=config.Defaults.GITHUB_OWNER.value,
        help='GitHub owner of the repository')
    new_project.add_argument(
        '--github-repo',
        default=config.Defaults.GITHUB_REPO.value,
        help='GitHub repository to use for the version')
    new_project.add_argument(
        '--image',
        default=config.Defaults.IMAGE_DEFAULT.value,
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
        '--last-versions',
        default=config.Defaults.LAST_VERSIONS_LIST.value,
        help='Max last release versions to query')
    list_version.add_argument(
        'image', action=ListVersionAction)

    # findver command
    find_version = subparsers.add_parser(
        'findver', help='Find the latest version of a package',
        parents=[parent_parser])
    find_version.add_argument(
        '--last-versions',
        default=config.Defaults.LAST_VERSIONS_FIND.value,
        help='Max last release versions to query')
    find_version.add_argument(
        'image', action=FindVersionAction)

    # build command
    build = subparsers.add_parser(
        'build', help='Build a container image',
        parents=[parent_parser])
    build.add_argument(
        "--tag-latest",
        default=config.Defaults.TAG_LATEST.value,
        action="store_true",
        help='Tag built image as latest')
    build.add_argument(
        'image', action=BuildAction)

    parser.parse_args()


def main():
    try:
        parse_args()
    except subprocess.CalledProcessError as error:
        logging.debug('Stack Trace: %s', error)
        logging.error('Unable to execute command: %s', error)
    # TODO: redo this
    raise SystemExit


if __name__ == "__main__":
    main()
