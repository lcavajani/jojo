# import abc
import argparse
import logging
import typing


class JojoAction(argparse.Action):
    '''
    Base class for specific actions.
    '''

    def _setup_logger(self, namespace: argparse.Namespace):
        '''
        Sets up the logger for use.

        :name namespace: The namespace for parsed args.
        '''
        level = namespace.log_level or 'info'
        logging.basicConfig(level=logging.getLevelName(level.upper()))

    def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            # values: str,
            values: typing.Optional[str],
            # values: typing.Any,
            option_string: typing.Optional[str]):
        '''
        Sets up for execution of action.

        :name parser: The argument parser in use.
        :name namespace: The namespace for parsed args.
        :name values: Values for the action.
        :name option_string: Option string.
        :raises: subprocess.CalledProcessError
        '''
        self._setup_logger(namespace)
        return self.run(parser, namespace, values, option_string)

    def run(self, parser, namespace, values, option_string):
        pass
