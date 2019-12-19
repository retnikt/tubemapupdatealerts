import email.utils
import json
from typing import TYPE_CHECKING

import requests
import twitter
from google.cloud import storage

if TYPE_CHECKING:
    from datetime import datetime

BASE_CONTENT_URL = "http://content.tfl.gov.uk/"
BUCKET_NAME = open("bucket_name.txt").read().strip()
NAMES = [
    (
        "London's rail and Tube services",
        "london-rail-and-tube-services-map.pdf",
    ),
    ("Night Tube and London Overground map", "standard-night-tube-map.pdf"),
]
_TWITTER_CREDENTIALS = json.load(open("twitter_credentials.json"))
storage_client = storage.Client()
twitter_client = twitter.Api(**_TWITTER_CREDENTIALS)
bucket = storage_client.bucket(BUCKET_NAME)


def _upload(url, filename, new_timestamp, raw_timestamp):
    # download existing version
    # (we make another request because previously it was only a HEAD request to
    #  get the modification date)
    response = requests.get(url)

    # upload the current version
    new_blob = bucket.blob(
        f"{filename}/{filename}-{new_timestamp:%Y-%m-%d-%H-%M-%S}.pdf"
    )
    new_blob.metadata = {"timestamp": raw_timestamp}
    new_blob.upload_from_string(
        response.content, content_type=response.headers["Content-Type"]
    )
    return new_blob


def tube_map_update_check(event, _):
    for name, filename in NAMES:
        if "data" in event:
            if event["data"] not in ("*", filename):
                continue
        url = BASE_CONTENT_URL + filename

        raw_timestamp = requests.head(url).headers["Last-Modified"]

        new_timestamp: datetime = email.utils.parsedate_to_datetime(
            raw_timestamp
        )
        stored_blobs = list(storage_client.list_blobs(BUCKET_NAME, prefix=name))

        if stored_blobs:
            # get the most recent stored version
            previous_blob = max(
                stored_blobs,
                key=lambda blob: email.utils.parsedate_to_datetime(
                    blob.metadata["timestamp"]
                ),
            )
            previous_timestamp: datetime = email.utils.parsedate_to_datetime(
                previous_blob.metadata["timestamp"]
            )
            # if it has changed
            if new_timestamp > previous_timestamp:
                new_blob = _upload(url, filename, new_timestamp, raw_timestamp)
                # log the change
                print(
                    "change in:",
                    name,
                    f"({filename})",
                    "changed at:",
                    new_timestamp,
                    "last change at:",
                    previous_timestamp,
                    "previous version:",
                    previous_blob.media_link,
                    "current version:",
                    new_blob.media_link,
                )

                # announce with a tweet
                # (including retarded
                twitter_client.PostUpdate(
                    f"{name} changed at {raw_timestamp}! "
                    f"This version: {new_blob.media_link} ; "
                    f"old version: {previous_blob.media_link} © TfL"
                )
            else:
                # no change
                print(f"no change in {name}")
        else:
            # no stored previous version of the map exists
            # upload the current version only
            _upload(url, filename, new_timestamp, raw_timestamp)


if __name__ == '__main__':
    import sys

    tube_map_update_check({
        "data": sys.argv[1]
    }, None)
