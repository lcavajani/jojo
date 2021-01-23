import argparse
import logging
import typing

import action
import config
import util

LOGGER = logging.getLogger(__name__)


class FindVersionAction(action.JojoAction):
    '''
    Finds the version of a package from OS repo or GIT.
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

        buildfile_path = config.get_buildfile_path(
            path=namespace.path,
            image_name=values)
        build_config = config.get_build_config(
            path=namespace.path,
            image_name=values)
        tag_build = build_config.get_tag_build()
        version_from = tag_build.version_from

        if tag_build is None:
            LOGGER.info('No tag_build configured')
            return

        if version_from:
            LOGGER.info('Using tag_build for %s', version_from.type.value)

            repository = util.get_class(
                package='version_finder',
                module=version_from.type.value,
                name=version_from.type.value)(version_from=version_from)

            # TODO: add semver
            version = repository.get_latest(
                    first_versions=namespace.first_versions)

        if version is not None:
            LOGGER.info('Found version, %s', version)
            # TODO: add tag build construction VERSION+GIT etc
            build_config.image.tag = version
            build_config.image.tag_build.version = version

            if not namespace.dry_run:
                with open(file=buildfile_path, mode='w') as buildfile:
                    build_config.to_fobj(fileobj=buildfile)
