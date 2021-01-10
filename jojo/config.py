import dataclasses
import enum
import os
import typing

import dacite
# import jsonschema
import yaml

import util


class Defaults(enum.Enum):
    """
    Default configuration options.
    """
    ARCH = "x86_64"
    ALPINE_PACKAGE = 'REPLACE_ALPINE_PACKAGE'
    ALPINE_REPO = 'REPLACE_ALPINE_REPO'
    ALPINE_VERSION_ID = 'REPLACE_ALPINE_VERSION_ID'
    BUILDER = 'podman'
    BUILDFILE_NAME = '.jojo.yaml'
    DOCKERFILE_NAME = 'Dockerfile'
    DRY_RUN = 'False'
    IMAGE_DEFAULT = 'registry:443/image:tag'
    GITHUB_OWNER = 'REPLACE_GITHUB_OWNER'
    GITHUB_REPO = 'REPLACE_GITHUB_REPO'
    LAST_VERSIONS_LIST = 10
    LAST_VERSIONS_FIND = 100
    LOG_LEVEL = 'info'
    TAG_LATEST = True


class EnvVar(enum.Enum):
    """
    Environment variables.
    """
    BUILDER = 'JOJO_BUILDER'
    DRY_RUN = 'JOJO_DRY_RUN'
    IMAGES_PATH = 'JOJO_IMAGES_PATH'
    LOG_LEVEL = 'JOJO_LOG_LEVEL'
    GITHUB_TOKEN = 'GITHUB_TOKEN'


class SourceType(enum.Enum):
    ALPINE = 'alpine'
    GITHUB = 'github'


class TagType(enum.Enum):
    TAG = 'TAG'
    VERSION = 'VERSION'
    VERSION_DATE = 'VERSION_DATE'
    VERSION_GIT = 'VERSION_GIT'


@dataclasses.dataclass
class Image:
    registry: str
    name: str
    tag: str

    @property
    def full_name(self):
        return util.image_full_name(
            self.registry,
            self.name,
            self.tag)

    @staticmethod
    def from_str(image: str) -> 'Image':
        # TODO: create func with ValueError to validate
        registry, name_tag = image.rsplit('/', 1)
        name, tag = name_tag.rsplit(':', 1)
        return Image(
            registry=registry,
            name=name,
            tag=tag,
        )


@dataclasses.dataclass
class VersionFromAlpine:
    package: str
    repository: str
    version_id: str
    arch: typing.Optional[str] = Defaults.ARCH.value
    type: SourceType = SourceType.ALPINE
    mirror: typing.Optional[str] = None
    semver: typing.Optional[str] = None
    version: typing.Optional[str] = None


@dataclasses.dataclass
class VersionFromGithub:
    owner: str
    repository: str
    type: SourceType = SourceType.GITHUB
    semver: typing.Optional[str] = None
    version: typing.Optional[str] = None


@dataclasses.dataclass
class TagBuild:
    version: typing.Optional[str]
    version_from: typing.Union[
        VersionFromAlpine,
        VersionFromGithub,
        None
    ] = None
    type: typing.Union[TagType] = TagType.TAG


@dataclasses.dataclass
class ImageTagFrom(Image):
    tag: typing.Optional[str]
    tag_build: typing.Optional[TagBuild]


@dataclasses.dataclass
class ImageBuildConfig:
    image: ImageTagFrom
    from_image: typing.Optional[Image] = None
    from_image_builder: typing.Optional[Image] = None

    @staticmethod
    def from_dict(image_config_dict: dict) -> 'ImageBuildConfig':
        image_config = dacite.from_dict(
            data_class=ImageBuildConfig,
            data=image_config_dict,
            config=dacite.Config(
                cast=[
                    SourceType,
                    TagType,
                ]
            )
        )

        return image_config

    def to_dict(self):
        return dataclasses.asdict(self)

    def to_yaml(self):
        raw_dict = self.to_dict()
        return yaml.dump(
            data=raw_dict,
            Dumper=EnumValueYamlDumper,
        )

    def to_fobj(self, fileobj: typing.TextIO):
        raw_dict = self.to_dict()
        yaml.dump(
            data=raw_dict,
            stream=fileobj,
            Dumper=EnumValueYamlDumper,
        )

    def get_tag_build(self):
        return self.image.tag_build


class EnumValueYamlDumper(yaml.SafeDumper):
    """
    a yaml.SafeDumper that will dump enum objects using their values.
    """
    def represent_data(self, data):
        if isinstance(data, enum.Enum):
            return self.represent_data(data.value)
        return super().represent_data(data)


def get_buildfile_path(path: str, image_name: str) -> str:
    """
    Returns the path of the buildfile.
    :param path: The path of the image directory.
    """
    image_dir = util.get_image_dir(path, image_name)
    buildfile = os.path.join(
        image_dir,
        Defaults.BUILDFILE_NAME.value)

    if not os.path.isfile(buildfile):
        raise ValueError(f'buildfile does not exist: {buildfile}')

    return buildfile


def get_build_config(
        path: str,
        image_name: str) -> typing.Optional[ImageBuildConfig]:
    """
    Returns an ImageBuildConfig object from the default buildfile
    located in the image directory.
    :param path: The path of the images directory.
    :param name: Name of the image, must exist as a directory.
    """
    buildfile_path = get_buildfile_path(path, image_name)
    return ImageBuildConfig.from_dict(
        util.load_yaml(
            buildfile_path
        )
    )
