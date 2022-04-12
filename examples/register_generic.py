#!/usr/bin/env python3
from datetime import datetime, timezone
from os import environ

from cybsi.api import Config, CybsiClient
from cybsi.api.observable import (
    AttributeNames,
    EntityForm,
    EntityKeyTypes,
    EntityTypes,
    RelationshipKinds,
    ShareLevels,
)
from cybsi.api.observation import GenericObservationForm


def create_generic_observation():
    domain = EntityForm(
        EntityTypes.DomainName,
        [(EntityKeyTypes.String, "test.com")],
    )
    ip_address = EntityForm(
        EntityTypes.IPAddress,
        [(EntityKeyTypes.String, "8.8.8.8")],
    )

    observation = (
        GenericObservationForm(
            share_level=ShareLevels.Green, seen_at=datetime.now(timezone.utc)
        )
        .add_attribute_fact(
            entity=domain,
            attribute_name=AttributeNames.IsIoC,
            value=True,
            confidence=0.9,
        )
        .add_attribute_fact(
            entity=domain,
            attribute_name=AttributeNames.IsMalicious,
            value=True,
            confidence=0.9,
        )
        .add_entity_relationship(
            source=domain,
            kind=RelationshipKinds.ResolvesTo,
            target=ip_address,
            confidence=0.5,
        )
    )
    return observation


if __name__ == "__main__":
    api_key = environ.get("CYBSI_API_KEY")
    api_url = environ.get("CYBSI_API_URL")

    config = Config(api_url, api_key=api_key, ssl_verify=False)

    with CybsiClient(config) as client:
        generic_observation = create_generic_observation()
        ref = client.observations.generics.register(generic_observation)
        view = client.observations.generics.view(ref.uuid)
