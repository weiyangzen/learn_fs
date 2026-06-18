# sources/storage-engines/pebble/scripts/code-coverage-publish.sh

## Purpose
This script turns LCOV artifacts into HTML coverage reports with `genhtml` and publishes them to a Google Cloud Storage bucket.

## Important APIs, Types, and Functions
`publish PROFILE TITLE` validates the profile, builds a timestamp/SHA/title output directory, copies the profile with a useful name, runs `genhtml`, and uploads the directory with `gsutil -m cp -Z -r`.

The script publishes tests-only, meta-only, and combined coverage profiles, then regenerates and uploads an index page.

## Control Flow
With `set -euxo pipefail`, it publishes three reports under `artifacts/`, lists existing bucket directories, emits an HTML index sorted newest first, uploads it, and sets short cache-control metadata.

## State and Persistence Behavior
Local generated state is under `artifacts/`. Remote persistent state is under `gs://$BUCKET/pebble`, with default bucket `crl-codecover-public`.

## Dependencies and Integration Points
It depends on `genhtml`, `gsutil`, git, date, sed, grep, and LCOV files produced by `code-coverage.sh`.

## Risks
Bucket permissions, missing tools, or malformed profile paths fail the script. The generated index is hand-built HTML, so unexpected bucket names could affect output. It assumes `date -r` behavior available in the environment.

## Test Signals
No direct tests are present; success is published coverage directories and refreshed bucket index.
