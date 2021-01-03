import argparse
import logging
import subprocess
import typing

import builder
import config
import util

LOGGER = logging.getLogger(__name__)


class Podman(builder.Builder):
    """
    Manage images with podman.
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
        build_args_images = get_build_args_images(build_config)
        version = build_config.image.tag_build.version

        command = Command(['podman', 'build', '-t'])
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


def get_build_args_images(build_config: config.ImageBuildConfig):
    args = []
    # if build_config.image:
    #     args.append(f'IMAGE={build_config.image.full_name}')
    if build_config.from_image:
        args.append(f'FROM_IMAGE={build_config.from_image.full_name}')
    if build_config.from_image_builder:
        args.append(f'FROM_IMAGE_BUILDER={build_config.from_image_builder.full_name}')
    return args


def get_build_args(build_config: config.ImageBuildConfig):
    build_config_dict = build_config.to_dict()
    args = []
    for k, v in build_config_dict.items():
        if k.startswith('from_image') and v is not None:
            args += [f'{k.upper()}_{r.upper()}={t}' for (r, t) in v.items() if isinstance(t, str)]

    return args


class Command(list):
    def add_arg(self, name: str):
        self.extend([name])

    def add_args(self, name: str, value: typing.Any):
        self.extend([name, value])

    def add_flag(self, name: str, value: bool):
        if value:
            self.append(name)

    def add_args_list(self, arg_name: str, list_values: list):
        for value in list_values:
            self.extend([arg_name, value])

    def __add__(self, other) -> "Command":
        return Command(super().__add__(other))
