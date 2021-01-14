import argparse
import logging
import subprocess

import builder
import config
import util

LOGGER = logging.getLogger(__name__)


class Buildah(builder.Builder):
    """
    Manage images with buildah.
    """

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
        build_args_images = builder.get_build_args_images(build_config)
        version = build_config.image.tag_build.version

        command = util.Command(['buildah', 'bud', '-t'])
        command.add_arg(image)
        command.add_args_list('--build-arg', build_args_images)

        if version:
            command.add_args('--build-arg', f'VERSION={version}')

        command.add_arg('.')

        LOGGER.info('Image name: %s', image)
        LOGGER.debug('Command: "%s"', ' '.join(command))

        if not namespace.dry_run:
            with util.pushd(image_dir):
                subprocess.check_call(command)

            if namespace.tag_latest:
                self.tag_latest(image)

    def tag_latest(self, image: str):
        '''
        :param image: The image to tag.
        '''
        self.tag(image, 'latest')

    def tag(self, image: str, tag: str):
        '''
        :param image: The image to tag.
        :param tag: The tag for the image.
        '''
        LOGGER.info('Tagging image')

        command = util.Command(['buildah', 'tag', image])
        name, _ = image.rsplit(':', 1)
        new_image = ':'.join([name, tag])
        command.add_arg(new_image)

        LOGGER.info('Image to tag: %s', image)
        LOGGER.info('Additional tag: %s', new_image)
        subprocess.check_call(command)
