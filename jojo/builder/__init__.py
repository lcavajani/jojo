import abc
import argparse

import config


class Builder(abc.ABC):
    '''
    Base class for image management.
    '''

    @abc.abstractmethod
    def build(
            self,
            namespace: argparse.Namespace,
            image: str,
            build_config: config.ImageBuildConfig):
        '''
        Builds a specific image.

        :param namespace: Namespace passed in via CLI.
        :param image: The image to build.
        :raises: subprocess.CalledProcessError
        '''
        pass


def get_build_args(build_config: config.ImageBuildConfig):
    args = []

    if build_config.image.build_args:
        b_args = build_config.image.build_args
        args += [f'{k.upper()}={v}'
                 for (k, v) in b_args.items() if isinstance(v, str)]

    if build_config.from_image:
        args.append(
            f'FROM_IMAGE={build_config.from_image.full_name}')

    if build_config.from_image_builder:
        args.append(
            f'FROM_IMAGE_BUILDER={build_config.from_image_builder.full_name}')

    return args


# def get_build_args(build_config: config.ImageBuildConfig):
#     build_config_dict = build_config.to_dict()
#     args = []
#     for k, v in build_config_dict.items():
#         if k.startswith('from_image') and v is not None:
#           args += [f'{k.upper()}_{r.upper()}={t}'
#                        for (r, t) in v.items() if isinstance(t, str)]

#     return args
