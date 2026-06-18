# sources/object-store/garage/src/api/s3/copy.rs

## Purpose
Implements S3 `CopyObject` and `UploadPartCopy`. It reuses existing Garage object data whenever safe, or streams source object bytes through decrypt/checksum/encrypt/write paths when metadata, encryption, checksum, or range requirements demand a physical rewrite.

## Important APIs, Types, And Functions
`handle_copy` is the `CopyObject` entry point. It parses copy-source preconditions, checksum algorithm headers, source object metadata, source and destination encryption, metadata directive behavior, and then chooses `handle_copy_metaonly` or `handle_copy_reencrypt`. `handle_upload_part_copy` copies a byte range from a source object into an existing multipart upload part. `get_copy_source` resolves `x-amz-copy-source`, checks read permission on the source bucket, and fetches the source object. `extract_source_info` selects the latest complete non-delete source version metadata. `Defragmenter` coalesces block fragments during part-copy to avoid writing many tiny destination blocks.

## Control Flow
`CopyObject` first checks `x-amz-copy-source-*` preconditions against the selected source version. It unwraps source metadata with copy-source SSE-C headers and derives destination encryption from normal SSE-C headers. It identifies multipart-ish source data by ETag shape or checksum type. If encryption is unchanged and no checksum recomputation is required, the metadata-only path creates a new object version pointing to the same inline bytes or version blocks. Otherwise it builds a source byte stream via `full_object_byte_stream` and calls `save_stream`.

`UploadPartCopy` decodes the destination upload ID, fetches source object and destination MPU concurrently, validates source preconditions and SSE-C keys, parses `x-amz-copy-source-range`, rejects inline source objects as too small, loads source version blocks, computes affected block subranges, creates a placeholder MPU part and empty version, then streams source blocks through optional decryption, defragmentation, encryption, checksum calculation, block writes, version writes, and block-ref writes.

## State And Persistence
Metadata-only copies insert a new destination object version. For block-backed data they also insert a new `Version`, duplicate block entries, and insert new `BlockRef` rows without reuploading block contents. The code intentionally writes the final object after version/block refs to avoid same-source-destination races that could drop reference counts too early. `UploadPartCopy` updates `mpu_table` twice: once with an unfinished part placeholder and once with final ETag/checksum/size. It writes part blocks under a new `Version` with a `MultipartUpload` backlink.

## Dependencies And Integration Points
The module integrates with `get.rs` for preconditions and source streaming, `put.rs` for `save_stream` and metadata extraction, `multipart.rs` for upload lookup and upload-id decoding, `encryption.rs` for SSE-C handling, block/version/object/mpu tables, and checksum helpers from `garage_api_common`.

## Risks And Test Signals
Risks include subtle checksum type migration behavior, source/destination encryption equivalence, range boundary handling, and consistency if a part-copy fails after placeholder state is written. The `Defragmenter` can change block grouping, so checksum and offset accounting are key. Tests cover XML serialization of copy responses, but not persistence, block reuse, encrypted copy, or part-copy range behavior.
