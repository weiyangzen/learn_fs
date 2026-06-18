# sources/object-store/garage/src/api/s3/put.rs

## Purpose
Implements S3 PutObject and the reusable object write pipeline used by normal PUT, POST object, multipart upload parts, and copy-rewrite paths. It chunks streams, computes/verifies checksums, encrypts data, writes blocks, records version/block references, enforces quotas, and finalizes object metadata.

## Important APIs, Types, And Functions
`handle_put` parses request metadata, checksums, trailer checksum algorithms, and SSE-C headers before calling `save_stream`. `save_stream` handles inline versus block-backed storage and returns `SaveStreamResult`. `check_quotas` enforces bucket object/byte limits. `read_and_put_blocks` is the streaming pipeline. `put_block_and_meta` writes one block plus version and block-ref metadata. `StreamChunker` creates block-sized chunks. `extract_metadata_headers` preserves standard headers, `x-amz-meta-*`, and validates `x-amz-website-redirect-location`. `next_timestamp` maintains monotonic object-version timestamps.

## Control Flow
`save_stream` reads the first block while fetching any existing object. If the first block is below `INLINE_THRESHOLD`, it finalizes checksums, checks quotas, encrypts inline bytes and metadata, and writes a complete inline object. Larger uploads write an uploading marker to `object_table`, create an empty `Version`, then call `read_and_put_blocks`. After streaming, checksums are verified or stored, quotas are checked, and the object marker is replaced with a complete `FirstBlock` version. `InterruptedCleanup` marks the object version aborted if a failure occurs before finalization.

`read_and_put_blocks` runs a four-stage pipeline: read chunks from client, hash plaintext for MD5/extra checksums, encrypt and BLAKE2-hash stored bytes, then write blocks with bounded concurrent storage-node RPCs while inserting `version_table` and `block_ref_table` records.

## State And Persistence
Small objects live fully in `object_table` inline data. Large objects use `object_table` for uploading/complete version state, `version_table` for block layout, `block_ref_table` for GC/reference tracking, and `block_manager` for actual block bytes. Bucket quota checks read `object_counter_table` and account for replacement diffs from previous object counts.

## Dependencies And Integration Points
Used by `multipart.rs`, `copy.rs`, and `post_object.rs`. Depends on Garage block manager, object/version/block-ref/counter tables, checksum receiver types, OpenTelemetry tracing, encryption, website redirect header constants, and API body helpers.

## Risks And Test Signals
Risks include partial writes leaving aborted markers or orphaned version/block metadata for repair, checksum interactions with encrypted ETags, trailer checksum timing, and quota checks after block upload for large objects. The concurrent pipeline depends on channel ordering and `FuturesOrdered`. No local unit tests are present; coverage must come from integration uploads, multipart, copy, and checksum tests.
