# sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_multipart.rs

## Purpose
Implements non-streaming multipart upload primitives: initiate, upload part, complete, and a fallback wrapper for access-denied multipart attempts.

## Important APIs, Types, and Functions
- `put_object_multipart` calls `put_object_multipart_no_stream`; on access denied it may fall back to single PUT if the object fits single PUT limits.
- `put_object_multipart_no_stream` computes part info, initiates upload, reads parts, hashes them, uploads each part, builds `CompleteMultipartUpload`, completes, and returns `UploadInfo`.
- `initiate_multipart_upload` sends `POST ?uploads`, validates internal source version UUID, and should parse `InitiateMultipartUploadResult`.
- `upload_part` validates size/part number/upload ID, sends `PUT ?partNumber&uploadId`, and returns `ObjectPart` from response headers.
- `complete_multipart_upload` sends `POST ?uploadId` with marshalled completion XML and returns `UploadInfo`.
- `UploadPartParams` bundles upload-part request fields.

## Control Flow and State Behavior
Multipart state lives remotely: initiate returns an upload ID, upload-part calls create part state, complete finalizes object state. Locally, parts are stored in a `HashMap<i64, ObjectPart>` then converted into sorted completion parts.

## Dependencies and Integration Points
Depends on checksum modes, hash utilities, S3 multipart DTOs, client constants, `RequestMetadata`, `ReaderImpl`, `UploadInfo`, `trim_etag`, UUID validation, and error-response helpers.

## Persistence
No local persistence. It mutates remote multipart upload and object state.

## Risks and Edge Cases
- `initiate_multipart_upload` returns `InitiateMultipartUploadResult::default()` instead of parsing the response body, so `upload_id` is likely empty and later calls fail.
- `complete_multipart_upload` sets `content_length: 100` instead of the actual XML length and returns a default `CompleteMultipartUploadResult` without parsing response body.
- Upload loops read the entire reader for every part instead of slicing by part size.
- `hash_sums["md5"]` and `hash_sums["sha256"]` indexing can panic if those keys are absent.
- There is no abort-multipart cleanup on part upload or complete failure.

## Test Signals
No inline tests. High-priority tests are initiate response parsing, completion body length/parsing, part slicing, upload-id validation, error cleanup/abort, and checksum combinations.
