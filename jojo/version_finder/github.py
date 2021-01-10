import dataclasses
import logging
import os
import typing

import requests

import util
import config
import version_finder

GITHUB_GRAPHQL_API = 'https://api.github.com/graphql'
LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Github(version_finder.FindVersion):
    version_from: config.VersionFromGithub

    def __post_init__(self):
        self.http = requests.Session()
        self.headers = self._define_headers()

    @staticmethod
    def _define_headers():
        token = os.environ.get(config.EnvVar.GITHUB_TOKEN.value, None)
        if token:
            return {"Authorization": "Bearer {}".format(token)}

    def _query(self, query=None, variables=None):
        """
        Execute a GraphQL query.
        """
        try:
            request = self.http.post(
                GITHUB_GRAPHQL_API,
                json={'query': query, 'variables': variables},
                headers=self.headers)
            request.raise_for_status()
            return request.json()
        except(ConnectionError, requests.HTTPError, requests.Timeout) as err:
            LOGGER.error('connection failed: %s', err)

    def _get_releases(self, first_versions: int) -> typing.Any:
        query = '''
        query($owner: String!, $repo: String!, $first: Int!) {
          repository(name: $repo, owner: $owner) {
            releases(first: $first, orderBy: {field: CREATED_AT, direction: DESC}) {
              nodes {
                tagName
                isPrerelease
              }
            }
          }
        }
        '''

        variables = {
            'owner': self.version_from.owner,
            'repo': self.version_from.repository,
            'first': int(first_versions),
        }

        results = self._query(query=query, variables=variables)

        if 'errors' in results:
            errors = results['errors']
            for err in errors:
                LOGGER.error(err)
            raise SystemExit(errors)

        return results

    def get_all(self, first_versions: int) -> version_finder.Versions:
        results = self._get_releases(first_versions=first_versions)
        if results['data']['repository']:
            releases = results['data']['repository']['releases']['nodes']
            stable = [r['tagName'] for r in releases if not r['isPrerelease']]
            unstable = [r['tagName'] for r in releases if r['isPrerelease']]

        return version_finder.Versions(
                stable=list(map(util.sanitize_version, stable or [])),
                unstable=list(map(util.sanitize_version, unstable or [])),
                match=None)

    def get_latest(self, first_versions: int) -> typing.Optional[str]:
        versions = self.get_all(first_versions=first_versions)
        version = versions.stable[0]
        if version:
            return version
