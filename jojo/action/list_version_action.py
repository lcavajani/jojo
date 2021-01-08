import argparse
import logging
import typing

import action
import config
import util

LOGGER = logging.getLogger(__name__)


class ListVersionAction(action.JojoAction):
    """
    List the available version of a package from OS repo or GIT.
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
        build_config = config.get_build_config(
            path=namespace.path,
            image_name=values)
        tag_build = build_config.get_tag_build()
        version_from = tag_build.version_from

        if tag_build is None:
            LOGGER.info('no tag_build configured')

        if tag_build and version_from:
            LOGGER.info('using tag_build for %s', version_from.type.value)
            LOGGER.debug(version_from)

            repository = util.get_class(
                package="version_finder",
                module=version_from.type.value,
                name=version_from.type.value)(version_from=version_from)

            versions = repository.get_all(
                    last_versions=namespace.last_versions)

            for v in [v for v in (versions.stable or [])]:
                LOGGER.info(f'stable: {v}')

            for v in [v for v in (versions.unstable or [])]:
                LOGGER.info(f'unstable: {v}')

            # TODO: add if a matched version
