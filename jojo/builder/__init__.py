import abc
import argparse

import config


class Builder(abc.ABC):
    """
    Base class for image management.
    """

    def _normalize_filename(self, data):
        """
        Replaces problematic chars in filesnames.

        :param data: The filename to normalize
        :type data: str
        :returns: A normalized filename
        :rtype: str
        """
        return data.replace(':', '-').replace('/', '-')

    @abc.abstractmethod
    def build(
            self,
            namespace: argparse.Namespace,
            image: str,
            build_config: config.ImageBuildConfig):
        """
        Builds a specific image.

        :param namespace: Namespace passed in via CLI.
        :param image: The image to build.
        :raises: subprocess.CalledProcessError
        """
        pass
