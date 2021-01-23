import argparse
# import copy
import logging
import subprocess

import builder
import config
import util

LOGGER = logging.getLogger(__name__)


class Buildkit(builder.Builder):
    '''
    Manage images with buildkit.
    '''
    def _create_command(
                self,
                namespace: argparse.Namespace,
                action: str,
                build_args: list):
        '''
        Creates the command for the buildkit builder.
        '''
        command = util.Command(['buildctl'])

        if namespace.addr:
            command.add_args(name='--addr', value=namespace.addr)

        command.add_arg(name=action)
        command.add_args(name='--frontend', value='dockerfile.v0')
        command.add_args(name='--local', value='context=.')
        command.add_args(name='--local', value='dockerfile=.')
        command.add_args_list(
            name='--opt',
            values=[f'build-arg:{arg}' for arg in build_args])

        return command

    def build(
            self,
            namespace: argparse.Namespace,
            image: str,
            build_config: config.ImageBuildConfig):
        '''
        :param namespace: Namespace passed in via CLI.
        :param image: The image to build.
        :param build_config: the image build configuration.
        :raises: subprocess.CalledProcessError
        '''
        LOGGER.info('Build image')

        image_dir = util.get_image_dir(namespace.path, image)
        image = build_config.image.full_name
        build_args = builder.get_build_args(build_config)

        version = build_config.image.tag_build.version
        if version:
            build_args.append(f'VERSION={version}')

        command = self._create_command(
            namespace=namespace,
            action='build',
            build_args=build_args)

        image_names_output = [image]

        image_tag = build_config.image.tag
        if namespace.tag_latest and image_tag != 'latest':
            image_latest = util.set_image_tag_latest(
                image=image)
            image_names_output.append(image_latest)

        names_output = ','.join([f'name={i}' for i in image_names_output])
        command.add_args(
            name='--output',
            value=f'type=image,{names_output},push={namespace.push}')

        LOGGER.info('Image name: %s', image)
        LOGGER.info('Command: %s', ' '.join(command))

        if namespace.dry_run:
            return

        with util.pushd(image_dir):
            subprocess.check_call(command)
