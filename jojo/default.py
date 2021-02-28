import enum


class Alpine(enum.Enum):
    '''
    Default Alpine configuration.
    '''
    PACKAGE = 'ALPINE_PACKAGE'
    REPO = 'ALPINE_REPO'
    VERSION_ID = 'ALPINE_VERSION_ID'
    MIRROR = 'http://dl-cdn.alpinelinux.org'


class Github(enum.Enum):
    '''
    Default GitHub configuration.
    '''
    OWNER = 'GITHUB_OWNER'
    REPO = 'GITHUB_REPO'


class Builder(enum.Enum):
    '''
    Default Builder configuration.
    '''
    NAME = 'podman'
    DOCKERFILE_NAME = 'Dockerfile'


class Image(enum.Enum):
    '''
    Default Image configuration.
    '''
    ARCH = 'x86_64'
    NAME = 'registry:443/image:tag'


class Config(enum.Enum):
    '''
    Default configuration options.
    '''
    BUILDFILE_NAME = '.jojo.yaml'
    DRY_RUN = 'False'
    FIRST_VERSIONS_LIST = 10
    FIRST_VERSIONS_FIND = 100
    LOG_LEVEL = 'info'
    TAG_LATEST = False


class EnvVar(enum.Enum):
    '''
    Environment variables.
    '''
    BUILDER = 'JOJO_BUILDER'
    DRY_RUN = 'JOJO_DRY_RUN'
    IMAGES_PATH = 'JOJO_IMAGES_PATH'
    LOG_LEVEL = 'JOJO_LOG_LEVEL'
    GITHUB_TOKEN = 'GITHUB_TOKEN'
