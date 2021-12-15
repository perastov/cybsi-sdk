"""Use this section of API to operate external databases.

External databases are systems outside of Cybsi. They can be queried by Cybsi
for information about entities. The result of such query an observation.
The observation typically provides new attributes for the requested entity and
relationships of the requested entity with other entities.
"""

from typing import List, Optional, Dict, Any
import uuid

from ..api import Nullable, _unwrap_nullable, Tag
from ..view import _TaggedRefView
from .. import RefView
from ..internal import BaseAPI, JsonObjectForm
from ..observable import EntityTypes


class ExternalDBsAPI(BaseAPI):
    """External databases API."""

    _path = "/enrichment/external-dbs"

    def view(self, db_uuid: uuid.UUID) -> "ExternalDBView":
        """Get the external database view.

        Note:
            Calls `GET /enrichment/external-dbs/{db_uuid}`.
        Args:
            db_uuid: External database uuid.
        Returns:
            View of the external database.
        Raises:
            :class:`~cybsi.api.error.NotFoundError`: External database not found.
        """
        path = f"{self._path}/{db_uuid}"
        r = self._connector.do_get(path=path)
        return ExternalDBView(r)

    def register(self, form: "ExternalDBForm") -> RefView:
        """Register external database.

        Note:
            Calls `POST /enrichment/external-dbs`.
        Args:
            form: Filled external database form.
        Returns:
            Reference to external database in API.
        Raises:
            :class:`~cybsi.api.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.api.error.SemanticError`: Form contains logic errors.
            :class:`~cybsi.api.error.ConflictError`:
                An external database with such data source is already registered.
        Note:
            Semantic error codes::
              * :attr:`~cybsi.api.error.SemanticErrorCodes.DataSourceNotFound`
        """
        r = self._connector.do_post(path=self._path, json=form.json())
        return RefView(r.json())

    def edit(
        self,
        db_uuid: uuid.UUID,
        tag: Tag,
        entity_types: Optional[List[EntityTypes]] = None,
        web_page_url: Nullable[str] = None,
        task_execution_timeout: Nullable[int] = None,
        task_execution_attempts_count: Nullable[int] = None,
    ) -> None:
        """Edit the external database.

        Note:
            Calls `PATCH /enrichment/external-dbs/{db_uuid}`.
        Args:
            db_uuid: External database uuid.
            tag: :attr:`ExternalDBView.tag` value. Use :meth:`view` to retrieve it.
            entity_types: Entity types list. Non-empty if not :data:`None`.
            web_page_url: Link to the public page of the external database.
                :data:`~cybsi.api.common.Null` resets URL to empty value.
                :data:`None` means URL is left unchanged.
            task_execution_timeout: Enricher task execution timeout, sec.
                Timeout must be in range [1;864000].
                :data:`~cybsi.api.common.Null` means that Cybsi can use default timeout.
                :data:`None` means timeout is left unchanged.
            task_execution_attempts_count:
                The maximum number of attempts to complete the task by the enricher.
                Count must be in range [1;1000].
                :data:`~cybsi.api.common.Null` means that Cybsi can use default count.
                :data:`None` means that count is left unchanged.
        Raises:
            :class:`~cybsi.api.error.InvalidRequestError`:
                Provided arguments have invalid values.
            :class:`~cybsi.api.error.NotFoundError`: External database not found.
            :class:`~cybsi.api.error.ResourceModifiedError`:
                External database changed since last request. Update tag and retry.
        """
        form: Dict[str, Any] = {}
        if entity_types is not None:
            form["entityTypes"] = [t.value for t in entity_types]
        if web_page_url is not None:
            form["webPageURL"] = _unwrap_nullable(web_page_url)
        if task_execution_timeout is not None:
            form["taskExecutionTimeout"] = _unwrap_nullable(task_execution_timeout)
        if task_execution_attempts_count is not None:
            form["taskExecutionAttemptsCount"] = _unwrap_nullable(
                task_execution_attempts_count
            )
        path = f"{self._path}/{db_uuid}"
        self._connector.do_patch(path=path, tag=tag, json=form)


class ExternalDBView(_TaggedRefView):
    @property
    def data_source(self) -> RefView:
        """Data source reference representing external database."""
        return RefView(self._get("dataSource"))

    @property
    def entity_types(self) -> List[EntityTypes]:
        """Entity types we can enrich in the external database."""
        return [EntityTypes(typ) for typ in self._get("entityTypes")]

    @property
    def web_page_url(self) -> Optional[str]:
        """Link to the public page of the external database."""
        return self._get_optional("webPageURL")

    @property
    def task_execution_timeout(self) -> Optional[int]:
        """Enricher task execution timeout, sec."""
        return self._get_optional("taskExecutionTimeout")

    @property
    def task_execution_attempts_count(self) -> Optional[int]:
        """The maximum number of attempts to complete the task by the enricher."""
        return self._get_optional("taskExecutionAttemptsCount")


class ExternalDBForm(JsonObjectForm):
    """External database form.

    This is the form you need to fill to register external database.

    Args:
        data_source_uuid: Data source identifier representing external database.
            Unique for external database.
        entity_types: Non-empty entity types list.
        web_page_url: Link to the public page of the external database.
        task_execution_timeout: Enricher task execution timeout, sec.
            Timeout must be in range [1;864000].
        task_execution_attempts_count: The maximum number of attempts
            to complete the task by the enricher. Count must be in range [1;1000].
    Usage:
        >>> import uuid
        >>> from cybsi.api.enrichment import ExternalDBForm
        >>> from cybsi.api.observable import EntityTypes
        >>> external_db = ExternalDBForm(
        >>>     data_source_uuid=uuid.UUID("4fd3126f-a0e8-4613-8dc5-cb449641adf2"),
        >>>     entity_types=[EntityTypes.DomainName, EntityTypes.IPAddress],
        >>> )
    """

    def __init__(
        self,
        data_source_uuid: uuid.UUID,
        entity_types: List[EntityTypes],
        web_page_url: Optional[str] = None,
        task_execution_timeout: Optional[int] = None,
        task_execution_attempts_count: Optional[int] = None,
    ):
        super().__init__()
        self._data["dataSourceUUID"] = str(data_source_uuid)
        self._data["entityTypes"] = [typ.value for typ in entity_types]
        if web_page_url is not None:
            self._data["webPageURL"] = web_page_url
        if task_execution_timeout is not None:
            self._data["taskExecutionTimeout"] = task_execution_timeout
        if task_execution_attempts_count is not None:
            self._data["taskExecutionAttemptsCount"] = task_execution_attempts_count
