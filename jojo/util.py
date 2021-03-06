from contextlib import contextmanager
import os
import importlib
import logging
import typing

import yaml

LOGGER = logging.getLogger(__name__)


class Command(list):
    def add_arg(self, name: str):
        self.append(name)

    def add_args(self, name: str, value: str):
        self.extend([name, value])

    def add_args_list(self, name: str, values: list):
        for value in values:
            self.extend([name, value])

    def __add__(self, other) -> 'Command':
        return Command(super().__add__(other))


def urljoin(*parts: str) -> str:
    if len(parts) == 1:
        return parts[0]
    first = parts[0]
    last = parts[-1]
    middle = parts[1:-1]

    first = first.rstrip('/')
    middle = list(map(lambda s: s.strip('/'), middle))
    last = last.lstrip('/')

    return '/'.join([first] + middle + [last])


def image_full_name(
        registry: str,
        name: str,
        tag: str) -> str:
    '''
    Build an image name.
    '''
    return urljoin(registry, f'{name}:{tag}')


def get_image_dir(path: str, image_name: str) -> str:
    '''
    Returns the path of the image directory
    :param path: The path of the images directory.
    :param name: Name of the image, must exist as a directory.
    '''
    image_dir = os.path.join(path, image_name)

    if not os.path.isdir(image_dir):
        raise ValueError(f'image directory does not exist: {image_dir}')

    return image_dir


def set_image_tag_latest(image: str) -> str:
    '''
    Set the image tag to latest.
    :param image: Full name of the image.
    '''
    name, _ = image.rsplit(':', 1)
    return ':'.join([name, 'latest'])


def load_yaml(path: str) -> typing.Any:
    '''
    Load file and read yaml.
    :param path: The path of the yaml file.
    '''
    try:
        with open(path, 'r', encoding='utf-8') as fobj:
            content = yaml.safe_load(fobj)
        return content
    except IOError as io_err:
        LOGGER.error('I/O error: %s', io_err)
    except yaml.YAMLError as yaml_err:
        LOGGER.error('Error in yaml file: %s', yaml_err)


def get_class(package: str, module: str, name: str) -> typing.Any:
    '''
    Returns a class.
    :param package: The name of the package.
    :param module: The name of the module.
    :param name: The name of the class.
    :raises: AttributeError
    :raises: ImportError
    '''
    mod = '{}.{}'.format(package, module)
    logging.debug('Importing %s', mod)
    cls = getattr(importlib.import_module(mod), name.capitalize())
    logging.debug('Class: %s', cls)
    return cls


@contextmanager
def pushd(path: str):
    '''
    Changes to a path until end of context.
    :param path: A file system path.
    '''
    original_cwd = os.getcwd()
    logging.info('Original dir: %s, Moving to %s', original_cwd, path)
    os.chdir(path)
    yield
    logging.info('Moving back to %s, from %s', original_cwd, path)
    os.chdir(original_cwd)


def get_first_key_dict(dico: dict) -> typing.Any:
    '''
    Returns the very first key from a dict.
    :param dico: The dict to iterate through.
    '''
    for key in dico:
        return key


def sanitize_version(version: str) -> str:
    '''
    Sanitizes the version.
    :param version: The version to sanitize.
    '''
    if version.startswith('v'):
        version = version[1:]
    return version
