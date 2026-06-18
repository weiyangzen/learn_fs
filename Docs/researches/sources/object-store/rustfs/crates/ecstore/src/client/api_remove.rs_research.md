# sources/object-store/rustfs/crates/ecstore/src/client/api_remove.rs

## Purpose
Implements S3 removal operations for the RustFS transition client: bucket delete, object delete, multi-object delete, and multipart-upload abort. It is the client-side HTTP/XML bridge between higher-level lifecycle/replication code and S3-compatible remote tiers.

## Important APIs, types, and functions
`RemoveBucketOptions`, `AdvancedRemoveOptions`, `RemoveObjectOptions`, `RemoveObjectsOptions`, `RemoveObjectResult`, and `RemoveObjectError` model deletion inputs and streamed outputs. `TransitionClient::remove_bucket`, `remove_bucket_with_options`, `remove_object`, `remove_object_inner`, `remove_objects`, `remove_objects_with_result`, `remove_objects_inner`, `remove_incomplete_upload`, and `abort_multipart_upload` are the main APIs. `generate_remove_multi_objects_request` serializes `<Delete>` XML and `process_remove_multi_objects_response` parses `<DeleteResult>` XML into per-object results.

## Control flow
Single bucket and object deletes construct `RequestMetadata` and call `execute_method` with HTTP DELETE, then clear bucket location cache for bucket deletes or extract delete marker headers for object deletes. Batch deletion consumes `ObjectInfo` values from a Tokio channel, groups up to 1000 entries, generates XML, computes MD5 and lowercase hex SHA-256 payload hashes, posts `?delete`, reads the response body, and sends one result per object. Invalid XML-name fallback is scaffolded but `has_invalid_xml_char` currently always returns false. Multipart abort maps a 404 into a typed `NoSuchUpload` response and otherwise propagates parsed HTTP errors.

## State and persistence behavior
This module does not persist local state. It mutates the in-memory bucket location cache after bucket deletion and emits deletion outcomes over channels. Remote S3/object-store state is changed by DELETE/POST requests. Batch deletion tracks a local pending set to detect missing response entries.

## Dependencies and integration points
It depends on `TransitionClient::execute_method`, `RequestMetadata`, S3 headers, `s3s::S3ErrorCode`, RustFS hash utilities, `ObjectInfo`, `DeleteMultiObjects`, and Tokio MPSC. It integrates with multipart upload discovery/abort APIs and with replication/lifecycle callers that consume result streams.

## Risks and edge cases
`remove_objects_with_result` creates a duplicate unused channel before creating the real one. `RemoveObjectResult::clone` drops the embedded error, so error forwarding can lose detail when a cloned result is sent. Batch response parsing requires one exact `(key, version)` match per input and reports synthetic errors for XML parse/read failures or unmatched entries. `remove_bucket_with_options` ignores its options, and response status validation for bucket/object delete relies mostly on `execute_method`.

## Test signals
The embedded Tokio test captures a raw HTTP request and asserts multi-delete uses a 64-character lowercase hex `X-Amz-Content-Sha256` instead of base64. Response parsing paths are covered indirectly by receiving at least one result from the local test server.
