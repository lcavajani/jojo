import argparse
import logging
import subprocess

import builder
import config
import util

LOGGER = logging.getLogger(__name__)


class Buildah(builder.Builder):
    '''
    Manage images with buildah.
    '''

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
        LOGGER.info('Dry Run: %s', namespace.dry_run)

        image_dir = util.get_image_dir(namespace.path, image)
        image = build_config.image.full_name
        build_args = builder.get_build_args(build_config)

        command = util.Command(['buildah', 'bud', '-t'])
        command.add_arg(image)
        command.add_args_list('--build-arg', build_args)

        version = build_config.image.tag_build.version
        if version:
            command.add_args('--build-arg', f'VERSION={version}')

        # add build context
        command.add_arg('.')

        LOGGER.info('Image name: %s', image)
        LOGGER.info('Command: %s', ' '.join(command))

        if namespace.dry_run:
            return

        # build
        with util.pushd(image_dir):
            subprocess.check_call(command)

        if namespace.tag_latest:
            self.tag_latest(image)

        self.push(
                namespace=namespace,
                image=image)

    def push(self, namespace: argparse.Namespace, image: str):
        '''
        :param image: The image to tag.
        :raises: subprocess.CalledProcessError
        '''
        LOGGER.info('Push image')
        LOGGER.info('Dry Run: %s', namespace.dry_run)
        LOGGER.info('Image to push: %s', image)

        command = util.Command(['buildah', 'push', image])
        LOGGER.info('Command: %s', ' '.join(command))

        if namespace.dry_run:
            return

        subprocess.check_call(command)

        if namespace.tag_latest:
            self.tag_latest(image)
            command[-1] = util.set_image_tag_latest(image=image)
            LOGGER.info('Command: %s', ' '.join(command))
            subprocess.check_call(command)

    def tag_latest(self, image: str):
        '''
        :param image: The image to tag.
        :raises: subprocess.CalledProcessError
        '''
        LOGGER.info('Tag image to latest')
        self._tag(image, 'latest')

    def _tag(self, image: str, tag: str):
        '''
        :param image: The image to tag.
        :param tag: The tag for the image.
        :raises: subprocess.CalledProcessError
        '''
        LOGGER.info('Tag image')

        command = util.Command(['buildah', 'tag', image])
        name, _ = image.rsplit(':', 1)
        new_image = ':'.join([name, tag])
        command.add_arg(new_image)

        LOGGER.info('Image to tag: %s', image)
        LOGGER.info('Additional tag: %s', new_image)
        LOGGER.info('Command: %s', ' '.join(command))
        subprocess.check_call(command)
