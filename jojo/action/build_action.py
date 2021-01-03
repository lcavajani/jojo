import argparse
import logging
import typing

import action
import config
import util

LOGGER = logging.getLogger(__name__)


class BuildAction(action.JojoAction):
    """
    Build an image.
    """

    def run(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str,
            option_string: typing.Optional[str]):
        """
        Execution of the action.
        :name parser: The argument parser in use.
        :name namespace: The namespace for parsed args.
        :name values: Values for the action.
        :name option_string: Option string.
        """
        build_config = config.get_build_config(
                path=namespace.path,
                image_name=values)

        LOGGER.debug(build_config)

        builder = util.get_class(
            package='builder',
            module=namespace.builder,
            name=namespace.builder)()

        builder.build(
            namespace=namespace,
            image=values,
            build_config=build_config)
