# sources/object-store/rustfs/crates/ecstore/src/client/api_put_object.rs

## Purpose
Defines put-object options and the top-level routing logic that chooses single PUT, multipart with known size, multipart without length, or parallel stream multipart based on object size, signer, and options.

## Important APIs, Types, and Functions
- `AdvancedPutOptions` carries replication source/version/etag/status/time metadata and internal replication flags.
- `PutObjectOptions` carries user metadata/tags, content headers, object lock settings, storage class, redirect, part size, checksum settings, multipart flags, and custom headers.
- `PutObjectOptions::header` converts options and user metadata into HTTP headers.
- `PutObjectOptions::validate` is currently a no-op.
- `TransitionClient::put_object` rejects unknown size with disabled multipart, then delegates.
- `put_object_common` enforces max size, sets default auto checksum, decides between `put_object_gcs`, `put_object_multipart`, `put_object_multipart_stream_parallel`, `put_object_multipart_stream_no_length`, or `put_object_multipart_stream`.
- `put_object_multipart_stream_no_length` initiates multipart upload for unknown-size input and uploads sequential parts.

## Control Flow and State Behavior
The route depends on `size`, `disable_multipart`, `concurrent_stream_parts`, `num_threads`, signer type, and computed/default part size. Unknown-size uploads require multipart unless parallel stream mode is selected. The no-length multipart path reads from `ReaderImpl`, computes MD5 or checksum headers, uploads parts, builds `CompleteMultipartUpload`, completes, and sets uploaded size.

## Dependencies and Integration Points
Depends on S3 DTOs and headers, checksum helpers, client constants, multipart APIs, `ReaderImpl`, `TransitionClient`, `UploadInfo`, `SignatureType`, and header classification helpers for user metadata.

## Persistence
No local persistence. Successful calls create/replace remote objects and multipart upload state on the target endpoint.

## Risks and Edge Cases
- The no-length multipart loop reads the entire `ReaderImpl` into `buf` on every iteration; with `Body` it reuses the whole body for every part rather than slicing by `part_size`.
- `total_parts_count` for unknown size is computed as maximum possible parts, so without EOF-aware reading the loop can over-upload or repeat data.
- `PutObjectOptions::header` unwraps metadata header values, so invalid user metadata values panic.
- Tags are stored but not emitted as tagging headers/query here.
- `validate` does not enforce checksum/signer/trailing-header constraints.

## Test Signals
No inline tests. Tests should cover routing decisions, header generation, invalid metadata values, unknown-size multipart EOF behavior, checksum header behavior, and integration with multipart completion.
