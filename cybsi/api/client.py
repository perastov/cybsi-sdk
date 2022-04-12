from dataclasses import dataclass
from typing import Callable, Optional, Union

from .artifact import ArtifactsAPI
from .auth import APIKeyAuth, APIKeysAPI
from .data_source import DataSourcesAPI, DataSourceTypesAPI
from .enrichment import EnrichmentAPI
from .error import CybsiError
from .internal import HTTPConnector, JsonObjectView
from .observable import ObservableAPI
from .observation import ObservationsAPI
from .replist import ReplistsAPI
from .report import ReportsAPI
from .search import SearchAPI
from .user import UsersAPI


@dataclass
class Config:
    """:class:`CybsiClient` config.

    Args:
        api_url: Base API URL.
        auth: Optional callable :class:`CybsiClient` can use to authenticate requests.
            In most cases it's enough to pass `api_key` instead of this.
        ssl_verify: Enable SSL certificate verification.
        api_key: API key. Forces client to use
            :class:`cybsi.api.auth.APIKeyAuth` for authentication.
            `auth` parameter is ignored.
    """

    api_url: str
    auth: Union[APIKeyAuth, Callable, None] = None
    ssl_verify: bool = True
    api_key: str = ""


class CybsiClient:
    """The main entry point for all actions with Cybsi REST API.

    As the client is low-level, it is structured around Cybsi REST API routes.
    Use properties of the client to retrieve handles of API sections.

    The client also follows Cybsi REST API input-output formats,
    providing little to no abstration from JSONs API uses.
    It's relatively easy to construct an invalid request,
    so use client's functions wisely.

    Hint:
        Use :class:`~cybsi.api.CybsiClient` properties
        to construct needed API handles. Don't construct sub-APIs manually.

        Do this:
            >>> from cybsi.api import CybsiClient
            >>> client = CybsiClient(config)
            >>> client.observations.generics.view(observation_uuid)
        Not this:
            >>> from cybsi.api.observation import GenericObservationsAPI
            >>> GenericObservationsAPI(connector).view(observation_uuid)

    Args:
        config: Client config.
    Usage:
        >>> from cybsi.api import APIKeyAuth, Config, CybsiClient
        >>> api_url = "http://localhost:80/api"
        >>> api_key = "8Nqjk6V4Q_et_Rf5EPu4SeWy4nKbVPKPzKJESYdRd7E"
        >>> config = Config(api_url, api_key=api_key)
        >>> client = CybsiClient(config)
        >>> client.observations
        <cybsi_sdk.client.observation.ObservationsAPI object at 0x7f57a293c190>
    """

    def __init__(self, config: Config):
        if config.auth is None and not config.api_key:
            raise CybsiError("No authorization mechanism configured for client")

        auth = APIKeyAuth("", config.api_key) if config.api_key else config.auth
        self._connector = HTTPConnector(
            base_url=config.api_url,
            auth=auth,
            ssl_verify=config.ssl_verify,
        )

    def __enter__(self) -> "CybsiClient":
        self._connector.__enter__()
        return self

    def __exit__(
        self,
        exc_type=None,
        exc_value=None,
        traceback=None,
    ) -> None:
        self._connector.__exit__(exc_type, exc_value, traceback)

    def close(self) -> None:
        """Close client and release connections."""
        self._connector.close()

    @property
    def artifacts(self) -> ArtifactsAPI:
        """Artifacts API handle."""
        return ArtifactsAPI(self._connector)

    @property
    def data_sources(self) -> DataSourcesAPI:
        """Data sources API handle."""
        return DataSourcesAPI(self._connector)

    @property
    def data_source_types(self) -> DataSourceTypesAPI:
        """Data source types API handle."""
        return DataSourceTypesAPI(self._connector)

    @property
    def enrichment(self) -> EnrichmentAPI:
        """Enrichment API handle."""
        return EnrichmentAPI(self._connector)

    @property
    def observable(self) -> ObservableAPI:
        """Observable API handle."""
        return ObservableAPI(self._connector)

    @property
    def observations(self) -> ObservationsAPI:
        """Observations API handle."""
        return ObservationsAPI(self._connector)

    @property
    def replists(self) -> ReplistsAPI:
        """Reputation lists API handle."""
        return ReplistsAPI(self._connector)

    @property
    def reports(self) -> ReportsAPI:
        """Reports API handle."""
        return ReportsAPI(self._connector)

    @property
    def search(self) -> SearchAPI:
        """Search API handle."""
        return SearchAPI(self._connector)

    @property
    def users(self) -> UsersAPI:
        """Users API handle."""
        return UsersAPI(self._connector)

    @property
    def api_keys(self) -> APIKeysAPI:
        """API-Keys API handle."""
        return APIKeysAPI(self._connector)

    def version(self) -> "VersionView":
        """Get API and server version information.

        Note:
            Calls `GET /version`.
        Returns:
            Version view.
        """

        path = "/version"
        resp = self._connector.do_get(path)
        return VersionView(resp.json())


class VersionView(JsonObjectView):
    """Version view."""

    @property
    def api_version(self) -> "Version":
        """API specification version."""
        return Version(self._get("apiVersion"))

    @property
    def server_version(self) -> "Version":
        """Server version."""
        return Version(self._get("serverVersion"))


class Version:
    """Version."""

    def __init__(self, version: str):
        self._version = version

        p1, self._build = version.split("+", 1) if "+" in version else (version, "")
        core, self._prerelease = p1.split("-", 1) if "-" in p1 else (p1, "")
        self._major, self._minor, self._patch = [int(p) for p in core.split(".", 2)]

    def __str__(self):
        return self._version

    @property
    def major(self) -> int:
        """Major part of version."""

        return self._major

    @property
    def minor(self) -> int:
        """Minor part of version."""

        return self._minor

    @property
    def patch(self) -> int:
        """Patch part of version."""

        return self._patch

    @property
    def prerelease(self) -> Optional[str]:
        """Prerelease part of version."""

        if self._prerelease != "":
            return self._prerelease
        return None

    @property
    def build(self) -> Optional[str]:
        """Build part of version."""

        if self._build != "":
            return self._build
        return None
