#!/usr/bin/env python3
import shutil
from io import StringIO, BytesIO
from os import environ
from zipfile import ZipFile

from cybsi.api import APIKeyAuth, Config, CybsiClient
from cybsi.api.artifact import ArtifactTypes
from cybsi.api.artifact.enums import ArtifactContentDownloadCompressionTypes


def main():
    api_key = environ.get("CYBSI_API_KEY")
    api_url = environ.get("CYBSI_API_URL")

    auth = APIKeyAuth(api_url, api_key, ssl_verify=False)
    config = Config(api_url, auth, ssl_verify=False)
    client = CybsiClient(config)

    # Upload artifact. We pass StringIO, but any file-like object will do.
    content = StringIO("artifact content")
    artifact_ref = client.artifacts.upload(
        "example.txt", content, artifact_type=ArtifactTypes.FileSample
    )
    print_zipped_content(client, artifact_uuid=artifact_ref.uuid)
    print_plain_content(client, artifact_uuid=artifact_ref.uuid)


def print_zipped_content(client, artifact_uuid):
    """Download artifact content as ZIP archive (protected by password),
    unpack it in memory, and print ZIP content.
    """
    archive_password = "p@ss"
    with client.artifacts.get_content(
        artifact_uuid,
        archive=ArtifactContentDownloadCompressionTypes.ZIP,
        archive_password=archive_password,
    ) as content:
        buffer = copy_artifact_content_to_mem(content.stream)

    zip_archive = ZipFile(buffer)
    zip_archive.setpassword(archive_password.encode())
    unzipped_content = {name: zip_archive.read(name) for name in zip_archive.namelist()}
    print("zipfile entry names and their content: ", unzipped_content)


def print_plain_content(client, artifact_uuid):
    """Download entire artifact content and print it."""
    with client.artifacts.get_content(artifact_uuid) as content:
        buffer = copy_artifact_content_to_mem(content.stream)
    print("plain artifact content: ", buffer.getvalue())


def copy_artifact_content_to_mem(artifact_content) -> BytesIO:
    buffer = BytesIO()
    shutil.copyfileobj(artifact_content, buffer, length=1024 * 1024)
    return buffer


def copy_artifact_content_to_file(local_filename, artifact_content) -> None:
    with open(local_filename, "wb") as f:
        shutil.copyfileobj(artifact_content, f, length=1024 * 1024)


if __name__ == "__main__":
    main()
