# sources/object-store/rustfs/crates/ecstore/src/client/api_list.rs

## Purpose
Provides transition-client list APIs, with only ListObjectsV2 query implemented. Other bucket/list/version/multipart listing entry points are explicit unsupported placeholders.

## Important APIs, Types, and Functions
- `list_buckets` returns `Unsupported`.
- `list_objects_v2_query` builds `list-type=2` requests with prefix, delimiter, continuation token, owner, metadata, start-after, encoding, max-keys, and custom headers. It parses `ListBucketV2Result`.
- Unsupported placeholders include `list_object_versions_query`, `list_objects_query`, `list_multipart_uploads_query`, `list_object_parts`, `find_upload_ids`, and `list_object_parts_query`.
- `ListObjectsOptions` stores version/list option flags and basic list parameters.
- `ListObjectsOptions::set` accepts string keys for prefix/start-after/max-keys/delimiter and boolean-like flags.
- `decode_s3_name` currently returns names unchanged, even for `encoding-type=url`.

## Control Flow and State Behavior
The V2 query path builds `RequestMetadata`, executes `GET`, checks for `200 OK`, buffers the full XML response, deserializes it, checks truncated responses have a continuation token, then decodes object names and common prefixes. State is local to the call.

## Dependencies and Integration Points
Depends on client S3 datatype DTOs, `TransitionClient`, `RequestMetadata`, credentials error types for placeholders, `BucketInfo`, HTTP/hyper body utilities, `quick_xml`, and `EMPTY_STRING_SHA256_HASH`.

## Persistence
No persistence. It reads remote bucket listing state.

## Risks and Edge Cases
Most list APIs are not implemented. `decode_s3_name` does not URL-decode despite requesting `encoding-type=url`, so keys containing escaped characters may be returned incorrectly. Full response buffering ignores imported size limits. `String::from_utf8(...).unwrap()` can panic on invalid XML bytes. Boolean parsing in `ListObjectsOptions::set` has unusual `vtrue` handling.

## Test Signals
No inline tests. Needed tests include V2 XML parsing, non-OK error conversion, truncated-without-token validation, URL decoding, invalid XML/UTF-8 handling, and behavior of unsupported methods.
