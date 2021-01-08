import collections
import dataclasses
import urllib.request
import tarfile
from io import BytesIO

import version_finder
import config
import util

ALPINE_OS = "alpine"
DEFAULT_ARCH = "x86_64"
DEFAULT_MIRROR = "http://dl-cdn.alpinelinux.org"
APKINDEX_FILENAME = "APKINDEX.tar.gz"


@dataclasses.dataclass
class Alpine(version_finder.FindVersion):
    version_from: config.VersionFromAlpine

    def __post_init__(self):
        self.repo = self.version_from.repository
        self.version_id = self.version_from.version_id
        self.arch = self.version_from.arch
        self.mirror = self.version_from.mirror

        if not self.version_id.startswith("v"):
            self.version_id = "v" + self.version_id

        if self.arch is None:
            self.arch = DEFAULT_ARCH

        if self.mirror is None:
            self.mirror = DEFAULT_MIRROR

    @property
    def apkindex_url(self) -> str:
        # http://dl-cdn.alpinelinux.org/alpine/v3.12/main/x86_64/APKINDEX.tar.gz
        return util.urljoin(
            self.mirror,
            ALPINE_OS,
            self.version_id,
            self.repo,
            self.arch,
            APKINDEX_FILENAME,
        )

    def _fetch_apkindex(self):
        # TODO add to utils with try/error
        # response = urllib.request.urlopen(self.apkindex_url)
        return urllib.request.urlopen(self.apkindex_url)
        # return response.read()

    def _parse_apkindex(self, lines, start):
        end_of_block_found = False
        pkg_ver = {}
        for i in range(start[0], len(lines)):
            # Check for empty line
            start[0] = i + 1
            line = lines[i]
            if not isinstance(line, str):
                line = line.decode()
            if line == "\n":
                end_of_block_found = True
                break

            if line.startswith("P:"):
                package = line.split(':')[1].rstrip("\n")
                pkg_ver["package"] = package

            if line.startswith("V:"):
                version = line.split(':')[1].rstrip("\n")
                pkg_ver["version"] = version

        if end_of_block_found:
            return pkg_ver

    def _parse(self):
        apkindex = self._fetch_apkindex()
        fobj = BytesIO(apkindex.read())
        with tarfile.open(fileobj=fobj, mode="r:gz") as tar:
            with tar.extractfile(tar.getmember("APKINDEX")) as handle:
                lines = handle.readlines()

        packages = collections.OrderedDict()
        start = [0]
        while True:
            block = self._parse_apkindex(lines, start)
            if not block:
                break
            packages[block["package"]] = block["version"]

        return packages

    def get_all(self, last_versions: int) -> version_finder.Versions:
        _ = last_versions
        packages = self._parse()
        stable = []
        if self.version_from.package in packages:
            # there is only one package per repo
            stable = [packages[self.version_from.package]]

        return version_finder.Versions(
            stable=stable,
            unstable=None,
            match=None)

    def get_latest(self, last_versions: int) -> version_finder.Versions:
        versions = self.get_all(last_versions=last_versions)
        version = versions.stable[0]
        if version:
            return version
