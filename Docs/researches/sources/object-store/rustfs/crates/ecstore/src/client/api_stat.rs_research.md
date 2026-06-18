# sources/object-store/rustfs/crates/ecstore/src/client/api_stat.rs

## Purpose
Implements metadata/stat APIs for buckets and objects: bucket existence probing, bucket versioning retrieval placeholder, and object HEAD/stat conversion.

## Important APIs, types, and functions
`TransitionClient::bucket_exists`, `get_bucket_versioning`, and `stat_object` are the exported methods. `stat_object` consumes `GetObjectOptions` and returns `transition_api::ObjectInfo` via `to_object_info`.

## Control flow
`bucket_exists` issues a HEAD bucket request and returns false on non-OK responses, otherwise true; it also reads and logs error response details when available. `get_bucket_versioning` sends `GET ?versioning`, reads the body, logs parsed error metadata, and currently returns `VersioningConfiguration::default()`. `stat_object` builds headers from options, adds internal replication/delete-marker headers, executes HEAD, interprets delete-marker and replication-ready headers, and returns either parsed object metadata or a minimal `ObjectInfo` for non-success/delete-marker cases.

## State and persistence behavior
There is no local persistence. The methods read remote bucket/object metadata and map HTTP headers into transient structs. Internal replication flags are transmitted as custom headers.

## Dependencies and integration points
The module uses `TransitionClient::execute_method`, `GetObjectOptions`, S3 headers `x-amz-delete-marker` and `x-amz-version-id`, UUID parsing, and common error conversion. It is part of read, replication, and delete-marker workflows.

## Risks and edge cases
`bucket_exists` returns true if `execute_method` itself returns an error, because only the `Ok(resp)` branch can return false. `get_bucket_versioning` ignores the returned XML and always returns default configuration. `stat_object` suppresses most non-OK statuses into default `ObjectInfo` instead of returning an error, which may hide authorization or missing-object failures from callers.

## Test signals
No local tests are present. Useful signals would cover HEAD 200 metadata conversion, delete-marker 405 handling with version IDs, replication-ready headers, missing bucket/object errors, and XML parsing for bucket versioning.
