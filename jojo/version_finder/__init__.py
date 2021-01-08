import abc
import typing


class FindVersion(abc.ABC):
    '''
    Base class for package version finding.
    '''
    @abc.abstractmethod
    def get_all(self, last_versions: int) -> 'Versions':
        raise NotImplementedError()

    @abc.abstractmethod
    def get_latest(self, last_versions: int) -> 'Versions':
        raise NotImplementedError()


class Versions(typing.NamedTuple):
    '''
    Default result that is consumed by the version actions.
    '''
    stable: typing.Optional[typing.List[str]]
    unstable: typing.Optional[typing.List[str]]
    match: typing.Optional[str]
