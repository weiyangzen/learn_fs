# sources/object-store/rustfs/crates/ecstore/src/store_api/readers.rs

## Purpose

`readers.rs` is the read/write stream adaptation layer for ecstore object I/O. It wraps upload streams in `PutObjReader`, builds `GetObjectReader` pipelines for normal, ranged, compressed, encrypted, and encrypted-plus-compressed object reads, and translates S3-visible byte ranges into the physical offsets that erasure/disk code should fetch. It also resolves server-side encryption material for RustFS-managed SSE, SSE-C, and MinIO-compatible metadata layouts, including rio-v2 DARE package alignment when the `rio-v2` feature is enabled.

## Important APIs, Types, and Functions

- `PutObjReader` owns a `HashReader` upload stream. `new`, `as_hash_reader`, `from_vec`, `size`, and `actual_size` provide a minimal adapter used by `ObjectIO::put_object` and multipart write APIs. `from_vec` computes a SHA-256 hex digest for non-empty in-memory data.
- `GetObjectReader` owns `Box<dyn AsyncRead + Unpin + Send + Sync>` plus the visible `ObjectInfo`. `new` returns `(reader, storage_offset, storage_length)`, allowing the storage layer to fetch only the needed physical byte span before applying read transforms. `read_all` is a convenience collector, and `AsyncRead` delegates to the boxed stream.
- `HTTPRangeSpec` models inclusive HTTP ranges and suffix ranges. `from_object_info` turns `ObjectOptions.part_number` into a plaintext range over multipart parts, using `actual_size` when present. `get_offset_length` and `get_length` validate and clamp ranges against visible resource size.
- `ReadPlan` is the internal planner. It records physical `storage_offset`, physical `storage_length`, visible `object_size`, and a `ReadTransform`.
- `ReadTransform` has `Plain`, `Compressed`, and `Encrypted` variants. The encrypted variant can additionally carry compression metadata so decryption, decompression, and final visible range slicing happen in the right order.
- `RangedDecompressReader` skips bytes in a sequential decompressed stream, then returns only the requested range. With `new_draining`, it drains the remaining stream after the requested bytes are returned to avoid upstream erasure-pipeline broken pipes.
- `StreamConsumer` drains an inner stream on drop for rio-v2 paths where downstream range readers may stop early.
- `SkipReader` discards a fixed number of bytes from an already-decrypted stream, mainly for DARE package interior offsets.
- Encryption helpers include `resolve_encryption_material`, `resolve_ssec_material`, `resolve_managed_material`, `normalize_managed_metadata`, `decrypt_local_sse_dek`, `decrypt_rustfs_local_sse_dek`, and, behind `rio-v2`, MinIO object-key unsealing helpers such as `try_unseal_minio_object_key`.
- Offset helpers include `get_compressed_offsets`, rio-v2 `get_encrypted_offsets`, `encrypted_plaintext_size`, `is_multipart_encrypted_object`, `multipart_plaintext_size`, and `multipart_part_numbers`.

## Control Flow

`GetObjectReader::new` delegates to `ReadPlan::build` and then `ReadPlan::into_reader`. Planning first injects a part-number range from `ObjectOptions` when no explicit HTTP range was supplied. It then determines whether the object is compressed via `ObjectInfo::compression_read_plan` and encrypted via `ObjectInfo::is_encrypted`. Active restore requests deliberately disable encryption and compression transforms so the restore path reads plain restored data with plain range semantics.

For compressed, unencrypted reads, planning computes the visible size with `ObjectInfo::get_actual_size`. A requested visible range is mapped through `get_compressed_offsets`, which walks multipart parts, uses per-part compression indexes when available, and returns a physical compressed offset plus a decompressed skip amount. The physical fetch length is `oi.size - physical_off` so decompression can continue from the located block to the end. `into_reader` then wraps the storage reader in `crate::rio::decompression_reader`, optionally `StreamConsumer`, and either `RangedDecompressReader` for partial visible ranges or `LimitReader` for full decompressed output.

For encrypted reads, planning first resolves material. SSE-C requires caller headers for algorithm, base64 key, and key MD5, and validates the supplied key against stored metadata. Managed SSE accepts RustFS metadata and, under `rio-v2`, MinIO-style metadata normalized into RustFS header names. If a global KMS service exists, it decrypts the encrypted DEK; otherwise local fallback decryption uses `__RUSTFS_SSE_SIMPLE_CMK`, `RUSTFS_SSE_S3_MASTER_KEY`, or an all-zero key. The planner derives plaintext size from encrypted original-size metadata, multipart part actual sizes, or compressed actual size. Ranged encrypted reads either fetch the whole object for legacy backends, map the requested plaintext offset to a DARE package boundary via `get_encrypted_offsets`, or, for encrypted compressed rio-v2 objects, use `get_compressed_offsets` to land on a compression block and DARE package boundary. `into_reader` constructs the correct rio decrypt reader, skips package-internal bytes if needed, decompresses if needed, and applies visible range slicing.

Plain reads are the simple fallback: `HTTPRangeSpec` is evaluated against `oi.size`; `storage_offset`, `storage_length`, and visible object size are all plain object values. No wrapper is added around the storage reader.

`RangedDecompressReader::poll_read` loops, reading into an internal scratch buffer, advancing `current_offset`, discarding bytes until `target_offset`, and then copying bounded bytes into the caller buffer until `target_length` is reached. If EOF appears before the target offset, it returns `UnexpectedEof`. Its drop path starts draining only after the target range has been returned.

## State and Persistence Behavior

This file does not persist object metadata itself, but it interprets persistent `ObjectInfo.user_defined` metadata and `ObjectInfo.parts` fields written elsewhere. Important persisted metadata includes compression scheme and actual-size headers, RustFS managed-encryption DEK/IV/context/original-size headers, SSE-C key MD5 and original-size headers, and MinIO internal encryption headers under `rio-v2`. The returned `GetObjectReader.object_info.size` is rewritten to the visible response size, while the original `ObjectInfo` metadata is cloned. No durable writes are performed; spawned drain tasks are transient runtime cleanup.

## Dependencies and Integration Points

The module depends on `tokio::io::AsyncRead`, `HashReader`, `LimitReader`, `ObjectInfo`, `ObjectOptions`, `CompressionAlgorithm`, `rustfs_rio`/`crate::rio` encryption and compression readers, `rustfs_kms` global encryption service, `rustfs_utils::http` SSE header constants, `rustfs_utils::path::path_join_buf`, `aes-gcm`, `base64`, `md5`, and rio-v2-only `hmac`, `sha2`, and `serde`. It is consumed by implementations of `ObjectIO::get_object_reader` and by tests that instantiate readers directly. Its `(storage_offset, storage_length)` output is a critical integration point with erasure-coded object retrieval because storage must pass the matching physical byte span into the reader pipeline.

## Risks and Edge Cases

- Range semantics cross three coordinate systems: visible plaintext, compressed stream, and encrypted DARE package offsets. Bugs here can return wrong bytes while still producing plausible lengths.
- Legacy encryption backends fetch the whole encrypted object for ranged reads, which is correct but potentially expensive for large objects.
- `local_sse_master_key` falls back to an all-zero key when no KMS or local key env var is configured. That supports compatibility/tests but is security-sensitive if accidentally relied on in production.
- Case-insensitive metadata lookup reduces compatibility risk, but metadata normalization has many feature-gated branches; non-rio-v2 builds cannot consume MinIO sealed-key variants.
- `RangedDecompressReader::new_with_drain` rejects `offset >= total_size`, so a zero-length range exactly at EOF is invalid even though some HTTP-style interpretations may allow an empty body.
- Drain tasks are spawned and not awaited; they intentionally clean up upstream readers but may hide downstream errors.
- `ObjectInfo::is_encrypted` can classify objects as encrypted from broad metadata prefixes. If metadata is incomplete, reads fail late with "encrypted object metadata is incomplete."

## Test Signals

The file has extensive in-module tests. They cover `HTTPRangeSpec` suffix and part-number behavior, compressed range physical offset planning, headerless MinIO/rio-v2 compression indexes, `RangedDecompressReader` normal, partial, zero-length, and out-of-bounds behavior, restore-request bypass of transforms, missing SSE-C header rejection, managed SSE full and ranged reads, local managed fallback, MinIO metadata compatibility under rio-v2, SSE-C full and ranged reads, sealed object-key reads, DARE package offset selection, and encrypted-plus-compressed range reads. These tests are strong signals for read-planning behavior but mostly use in-memory cursors rather than full erasure backend integration.
