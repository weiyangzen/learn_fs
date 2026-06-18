# sources/storage-engines/foundationdb/fdbclient/tests/gcp_fixture.sh

## Purpose
This fixture configures blobstore tests to run against Google Cloud Storage. It creates scratch space, writes a GCS bearer-token credential file, returns host/bucket/credential configuration, and removes scratch data on shutdown.

## Important APIs, Types, And Functions
The public functions are `shutdown_gcp`, `create_gcp_dir`, `write_gcp_blob_credentials`, and `gcp_setup`. `gcp_setup` requires `GCS_APPLICATION_TOKEN` and `GCS_FDB_BUCKET`.

## Control Flow
Callers source the fixture, create a scratch directory, and call `gcp_setup build_dir scratch`. Setup validates required environment variables, chooses `storage.googleapis.com`, writes `{"accounts":{"@storage.googleapis.com":{"token":...}}}`, and prints `@host`, bucket, and credential-file path.

## State And Persistence Behavior
The fixture persists only a local credentials JSON file under the test scratch directory. It does not manipulate GCS buckets or objects directly.

## Dependencies And Integration Points
It integrates with `tests_common.sh` blobstore-provider selection and downstream blobstore URL construction using query parameter `p=gcs`. It depends on environment-provided credentials rather than cloud metadata APIs.

## Risks And Edge Cases
The credential JSON is constructed by string interpolation without escaping, so tokens containing JSON-significant characters could break the file. `gcp_setup` exits the parent script on missing environment variables. The `build_dir` parameter is accepted but unused.

## Test Signals
Expected signals are correct credentials-file creation, host returned with `@` prefix, selected bucket from `GCS_FDB_BUCKET`, and successful downstream `s3client` or bulkload operations in GCS provider mode.
