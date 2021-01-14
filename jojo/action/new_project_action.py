import argparse
import logging
import os
import typing

import jinja2

import action
import config
import default

LOGGER = logging.getLogger(__name__)


class NewProjectAction(action.JojoAction):
    '''
    Creates a new image project.
    '''

    def run(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str,
            option_string: typing.Optional[str]):
        '''
        :name parser: The argument parser in use.
        :name namespace: The namespace for parsed args.
        :name values: Values for the action.
        :name option_string: Option string.
        '''
        LOGGER.info('templating Dockerfile')
        tmpl = jinja2.Template(dockerfile_j2)
        dockerfile_rendered = tmpl.render(
            from_image_builder=namespace.from_image_builder,
            image_name=values,
            alpine_package=namespace.alpine_package,
            github_owner=namespace.github_owner,
            github_repo=namespace.github_repo,
        )
        LOGGER.debug('\n%s\n', dockerfile_rendered)

        try:
            LOGGER.info('creating build config')
            image = config.Image.from_str(
                namespace.image)

            version_from = None
            version_from_ctor = None
            if namespace.version_from:
                version_from_ctor = getattr(
                    config,
                    'VersionFrom' + namespace.version_from.capitalize(),
                    None)

            if version_from_ctor:
                if namespace.version_from == config.SourceType.GITHUB.value:
                    version_from = version_from_ctor(
                        owner=namespace.github_owner,
                        repository=namespace.github_repo)

                if namespace.version_from == config.SourceType.ALPINE.value:
                    version_from = version_from_ctor(
                        package=namespace.alpine_package,
                        repository=namespace.alpine_repo,
                        version_id=namespace.alpine_version_id)

            build_config = config.ImageBuildConfig(
                image=config.ImageTagFrom(
                    registry=image.registry,
                    name=image.name,
                    tag=image.tag,
                    tag_build=config.TagBuild(
                        version=None,
                        type=config.TagType.VERSION,
                        version_from=version_from,
                    ),
                )
            )
            if namespace.from_image:
                build_config.from_image = config.Image.from_str(
                    namespace.from_image)

            if namespace.from_image_builder:
                build_config.from_image_builder = config.Image.from_str(
                    namespace.from_image_builder)
            LOGGER.debug('\n%s', build_config.to_yaml())
        except TypeError:
            raise SystemError()

        # TODO: validate image name
        image_dir = os.path.join(namespace.path, values)
        buildfile_path = os.path.join(
            image_dir,
            default.Config.BUILDFILE_NAME.value)
        dockerfile_path = os.path.join(
            image_dir,
            default.Builder.DOCKERFILE_NAME.value)

        if namespace.dry_run:
            return

        try:
            LOGGER.info('creating image directory')
            os.mkdir(image_dir)
        except FileExistsError:
            LOGGER.info('the image directory already exists: %s', image_dir)

        LOGGER.info('writing build config')
        if os.path.isfile(buildfile_path):
            LOGGER.info('the build config file already exists: %s',
                        buildfile_path)
        with open(file=buildfile_path, mode='w') as buildfile:
            build_config.to_fobj(fileobj=buildfile)

        LOGGER.info('writing dockerfile')
        if os.path.isfile(dockerfile_path):
            LOGGER.info('the docker file already exists: %s',
                        dockerfile_path)
        with open(file=dockerfile_path, mode='w') as dockerfile:
            dockerfile.write(dockerfile_rendered)


dockerfile_j2 = '''
{%- if from_image_builder -%}
ARG FROM_IMAGE_BUILDER
{% endif -%}
ARG FROM_IMAGE

{% if from_image_builder -%}
FROM ${FROM_IMAGE_BUILDER} AS builder

ARG VERSION

RUN apk add --no-cache git make curl gcc libc-dev ncurses

RUN curl -OL "https://github.com/{{ github_owner }}/{{ github_repo }}/archive/v${VERSION}.tar.gz" && \\
    tar zxf "v${VERSION}.tar.gz" && cd "{{ image_name }}-${VERSION}" && \\
    make && mv ./{{ image_name }} /go/bin/{{ image_name }}
{% endif %}

FROM ${FROM_IMAGE}

{% if not from_image_builder %}
ARG VERSION
{% endif %}

LABEL maintainer="_me@spiarh.fr"

{% if from_image_builder %}
COPY --from=builder /go/bin/{{ image_name }} /usr/local/bin/{{ image_name }}
{% endif %}

RUN apk add --no-cache "{{ alpine_package }}~=${VERSION}"

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
'''  # noqa: E501
