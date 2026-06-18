# sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_streaming.rs

## Purpose
Implements streaming and single-PUT object upload paths: known-size multipart streaming, optional checksum mode, parallel streaming, Google/single PUT style upload, and the low-level `put_object_do`.

## Important APIs, Types, and Functions
- `UploadedPartRes` and `UploadPartReq` are small part-result/request structs.
- `put_object_multipart_stream` routes to parallel, read-at, or optional-checksum multipart stream path.
- `put_object_multipart_stream_from_readat` adjusts checksum options then delegates.
- `put_object_multipart_stream_optional_checksum` uploads parts sequentially with MD5 or auto-checksum headers, completes multipart, and validates total uploaded size.
- `put_object_multipart_stream_parallel` attempts concurrent part uploads using buffer and error channels, an `RwLock<HashMap>` for parts, and `join_all`.
- `put_object_gcs` is the single PUT wrapper.
- `put_object_do` builds and executes the final `PUT` request and maps response headers to `UploadInfo`.

## Control Flow and State Behavior
Known-size streaming computes part count/size, initiates upload, removes checksum-algorithm metadata, reads part buffers from `ReaderImpl`, uploads parts, builds completion XML, applies aggregate checksum metadata, completes, and sets uploaded size. Parallel mode preallocates buffers through a channel, spawns async upload futures, collects results, and completes once all futures resolve. Single PUT sends the provided reader directly through `execute_method`.

## Dependencies and Integration Points
Depends on checksum helpers (`add_auto_checksum_headers`, `apply_auto_checksum`), multipart primitives (`UploadPartParams`, `upload_part`, `complete_multipart_upload`), constants, request metadata, UUID validation for source version IDs, cancellation tokens, channels, and response header parsing for version/expiration/checksums.

## Persistence
No local persistence. It writes remote object data and multipart upload state.

## Risks and Edge Cases
- Multiple loops use `for i in 1..part_number` where `part_number == total_parts_count`, which omits the final part from completion.
- Sequential and parallel paths read the entire reader into each part buffer rather than bounded `part_size` chunks.
- Parallel preallocated buffers are created with capacity but length zero, then code expects `buf.len() == part_size`, causing immediate errors before reading.
- `join_all` results are not inspected; errors are expected through a side channel and can be missed.
- No abort-multipart cleanup on failure.
- Expiration header parsing uses `unwrap`, so malformed expiration headers panic.
- `put_object_do` only accepts `200 OK`; S3 PUT Object commonly returns `200 OK`, but compatibility with other success statuses should be explicit.

## Test Signals
No inline tests. Tests should cover part inclusion, actual chunked reads, parallel buffer behavior, error propagation from futures, multipart abort on failure, checksum aggregation, and single-PUT response header parsing.
