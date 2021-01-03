import argparse
import logging
import os
import typing

import jinja2

import action
import config

LOGGER = logging.getLogger(__name__)


class NewProjectAction(action.JojoAction):
    """
    Creates a new image project.
    """

    def run(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str,
            option_string: typing.Optional[str]):
        """
        :name parser: The argument parser in use.
        :name namespace: The namespace for parsed args.
        :name values: Values for the action.
        :name option_string: Option string.
        """
        LOGGER.info('templating Dockerfile')
        tmpl = jinja2.Template(dockerfile_j2)
        dockerfile_rendered = tmpl.render(
            from_image_builder=namespace.from_image_builder,
            image_name=values,
        )
        LOGGER.debug('\n%s\n', dockerfile_rendered)

        try:
            LOGGER.info('creating build config')
            image = config.Image.from_str(
                    namespace.image)

            build_config = config.ImageBuildConfig(
                image=config.ImageTagFrom(
                    registry=image.registry,
                    name=image.name,
                    tag=image.tag,
                    tag_build=config.TagBuild(
                        version=None,
                        type=config.SourceType.GITHUB,
                        # TODO: add tag_build
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

        # TODO: sanitize image name
        image_dir = os.path.join(namespace.path, values)
        buildfile_path = os.path.join(image_dir, config.Defaults.BUILDFILE_NAME.value)
        dockerfile_path = os.path.join(image_dir, config.Defaults.DOCKERFILE_NAME.value)

        dry_run = namespace.dry_run
        try:
            LOGGER.info('creating image directory')
            if not dry_run:
                os.mkdir(image_dir)
        except FileExistsError:
            LOGGER.info('the image directory already exists: %s', image_dir)

        LOGGER.info('writing build config')
        # if not os.path.isfile(buildfile_path) and not dry_run:
        if True:
            with open(file=buildfile_path, mode='w') as buildfile:
                build_config.to_fobj(fileobj=buildfile)
        else:
            LOGGER.info('the build config file already exists: %s', buildfile_path)

        LOGGER.info('writing dockerfile')
        # if not os.path.isfile(dockerfile_path) and not dry_run:
        if True:
            with open(file=dockerfile_path, mode='w') as dockerfile:
                dockerfile.write(dockerfile_rendered)
        else:
            LOGGER.info('the docker file already exists: %s', dockerfile_path)


dockerfile_j2 = '''
{%- if from_image_builder -%}
ARG FROM_IMAGE_BUILDER
{% endif -%}
ARG FROM_IMAGE

{% if from_image_builder -%}
FROM ${FROM_IMAGE_BUILDER} AS builder

ARG VERSION

RUN apk add --no-cache git make curl gcc libc-dev ncurses

RUN curl -OL "https://github.com/REPLACE_OWNER/REPLACE_REPO/archive/v${VERSION}.tar.gz" && \\
    tar zxf "v${VERSION}.tar.gz" && cd "{{ image_name }}-${VERSION}" && \\
    make && mv ./{{ image_name }} /go/bin/{{ image_name }}
{% endif %}

FROM ${FROM_IMAGE}

LABEL maintainer="_me@spiarh.fr"

{% if from_image_builder %}
COPY --from=builder /go/bin/{{ image_name }} /usr/local/bin/{{ image_name }}
{% endif %}

RUN apk add --no-cache REPLACE_ME

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
'''
