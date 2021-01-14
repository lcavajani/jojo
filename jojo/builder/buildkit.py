import argparse
# import copy
import logging
import subprocess

import builder
import config
import util

LOGGER = logging.getLogger(__name__)


class Buildkit(builder.Builder):
    """
    Manage images with buildkit.
    """
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
        """
        :param namespace: Namespace passed in via CLI.
        :param image: The image to build.
        :param build_config: the image build configuration.
        :raises: subprocess.CalledProcessError
        """
        LOGGER.info('Building image')

        image_dir = util.get_image_dir(namespace.path, image)
        image = build_config.image.full_name
        build_args = builder.get_build_args_images(build_config)

        version = build_config.image.tag_build.version
        if version:
            build_args.append(f'VERSION={version}')

        command = self._create_command(
                namespace=namespace,
                action='build',
                build_args=build_args)
        command.add_args(
                name='--output',
                value=f'type=image,name={image},push={namespace.push}')

        LOGGER.info('Image name: %s', image)
        LOGGER.info('Command: "%s"', ' '.join(command))

        # there is not tag command so just run the same command with latest tag
        # and reuse the build cache.
        if namespace.tag_latest:
            command_latest = self._create_command(
                    namespace=namespace,
                    action='build',
                    build_args=build_args)
            name, _ = image.rsplit(':', 1)
            image_latest = ':'.join([name, 'latest'])
            command_latest.add_args(
                    name='--output',
                    value=f'type=image,name={image_latest},push={namespace.push}')

            LOGGER.info('Image name: %s', image_latest)
            LOGGER.info('Command: "%s"', ' '.join(command_latest))

        if not namespace.dry_run:
            with util.pushd(image_dir):
                subprocess.check_call(command)

        if not namespace.dry_run and namespace.tag_latest:
            with util.pushd(image_dir):
                subprocess.check_call(command_latest)
