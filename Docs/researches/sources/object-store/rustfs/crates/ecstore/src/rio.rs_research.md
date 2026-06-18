# sources/object-store/rustfs/crates/ecstore/src/rio.rs

## Purpose

`rio.rs` is the ECStore read/write I/O compatibility facade over two RustFS RIO implementations. With the `rio-v2` feature it re-exports `rustfs_rio_v2`; otherwise it re-exports `rustfs_rio`. Around those exports, it provides stable helper functions for compression metadata, compression index encoding/decoding, compression/decompression reader selection, encryption/decryption reader selection, and write-pipeline composition.

The file’s main job is to let higher-level object code handle legacy streams and MinIO-compatible rio-v2 S2 streams with one interface. It also preserves legacy behavior when `rio-v2` is not enabled.

## Important APIs, Types, and Functions

`backend_name` returns `"rio-v2"` or `"legacy-rio"` according to the compile-time feature. `compression_metadata_value` returns the MinIO S2 scheme string (`klauspost/compress/s2`) under rio-v2 and the algorithm string under legacy mode.

`compression_scheme_to_algorithm` maps metadata strings to `CompressionAlgorithm`. Under rio-v2, the MinIO S2 scheme maps to the default algorithm placeholder because the v2 path routes compressed handling through S2 readers. Other strings are parsed with `CompressionAlgorithm::from_str`.

`ReadCompressionBackend` (`Legacy`, `V2`) and `compression_scheme_to_read_plan` split metadata interpretation into an algorithm plus a concrete decompressor backend. This allows v2 builds to read both new S2 metadata and older algorithm strings.

`ReadEncryptionBackend` (`Legacy`, `V2`) does the same for decryption call sites. `decrypt_reader`, `decrypt_reader_with_object_key`, `decrypt_multipart_reader`, and `decrypt_multipart_reader_with_object_key` choose between legacy nonce-based APIs and rio-v2 sequence/object-key APIs, while returning boxed `AsyncRead` trait objects.

`compression_index_storage_bytes` serializes an `Index` for metadata/storage. In rio-v2 builds it delegates to MinIO-compatible index storage bytes; otherwise it stores `Index::into_vec()`. `decode_compression_index_bytes` first tries the v2 MinIO decoder when available, then the legacy `Index::load`, then a rio-v2-only repair path that restores legacy S2 index framing headers before another legacy load attempt.

`compression_reader` creates a `CompressReader`. In rio-v2 builds it calls `CompressReader::with_encrypted_padding` when compression will be followed by encryption, so S2 streams receive padding frames suitable for encrypted MinIO-compatible layout. In legacy builds, the `encrypted` flag is ignored.

`decompression_reader` returns a boxed decompressor selected by `ReadCompressionBackend`; legacy builds ignore the backend and always use `rustfs_rio::DecompressReader`.

`WriteEncryption` is a small constructor-backed configuration object for write encryption. It supports singlepart object-key mode, singlepart key+base-nonce mode, multipart legacy key+base-nonce+part-number mode, and multipart object-key mode. The internal `WriteEncryptionMode` enum is private.

`WritePlan` composes optional compression and optional encryption around a `HashReader`. `new`, `with_compression`, `with_encryption`, and `is_passthrough` describe the plan. `apply` wraps compression first, then encryption, preserving the `HashReader::SIZE_PRESERVE_LAYER` sizing contract and passing through the caller-provided `actual_size`.

## Control Flow

Compile-time feature gates determine the underlying exported crate and many branch bodies. In a legacy build, most facade functions are thin wrappers over `rustfs_rio`. In a rio-v2 build, metadata and reader selection become compatibility decisions: MinIO S2 compression metadata maps to the v2 backend, while legacy algorithm strings still map to legacy decompression.

For reads, call sites can parse object compression metadata via `compression_scheme_to_read_plan`, build a decompressor with `decompression_reader`, and build a decryptor with the appropriate `decrypt_*` helper. The facade keeps the caller from directly depending on both rio crates in most cases.

For writes, callers build a `WritePlan`. `apply` first wraps the input `HashReader` in a compression reader if requested. It passes whether encryption is also configured so rio-v2 can add encrypted S2 padding. Then it wraps the result in the requested encryption mode. Object-key encryption modes use v2 object-key APIs when available and fall back to legacy nonce-zero APIs without the feature.

For compression index persistence and reads, `compression_index_storage_bytes` writes the format appropriate to the active feature. `decode_compression_index_bytes` is deliberately permissive: v2 MinIO format, direct legacy format, and restored-header legacy format can all decode to an `Index`.

## State and Persistence Behavior

The file itself owns no durable state. Its persistence impact is indirect through metadata and object bytes produced by compression/encryption readers. The stable metadata-facing values are compression scheme strings and serialized compression indexes.

Under rio-v2, newly written compressed metadata uses the MinIO S2 scheme string regardless of the `CompressionAlgorithm` argument. New index bytes use `minio_index_storage_bytes`. Compatibility reads still attempt to decode legacy `Index` bytes and v2 headerless/header-restored shapes.

`WritePlan::apply` preserves size metadata through `HashReader::from_reader` wrappers. This is significant because surrounding object-storage code relies on `HashReader` for checksums, sizes, and optional compression indexes.

## Dependencies and Integration Points

The module re-exports either `rustfs_rio_v2` or `rustfs_rio`, so downstream ECStore modules can import RIO types from this facade. It depends on `bytes::Bytes`, `rustfs_utils::CompressionAlgorithm`, `tokio::io::AsyncRead`, and the `HashReader`, `CompressReader`, `DecompressReader`, `EncryptReader`, `DecryptReader`, and `Index` types provided by the selected RIO crates.

The compression scheme string matches MinIO S2 metadata, making this file part of object metadata interoperability. Encryption helpers encode compatibility assumptions for legacy nonce-based encryption, rio-v2 sequence-number decryption, and object-key encryption.

## Risks and Edge Cases

The rio-v2 metadata path intentionally ignores the provided compression algorithm for `compression_metadata_value` and maps MinIO S2 to `CompressionAlgorithm::default()`. That is correct only while v2 compressed objects are S2-only; future algorithm support would need to revisit this.

Legacy fallback for object-key encryption uses a zero nonce with the object key. That preserves old API shape but is not equivalent to rio-v2 object-key semantics unless the legacy implementation expects that convention.

Reader helper return types are boxed trait objects for read-side decompression/decryption, trading dynamic dispatch for uniform call sites. Write-side `WritePlan::apply` stays in `HashReader`, so changes in `HashReader::from_reader` sizing/index behavior can affect all compressed/encrypted writes.

`restore_legacy_index_headers` synthesizes S2 framing around raw bytes and mutates the chunk length bytes after construction. That compatibility repair is low-level and easy to break if S2 index framing assumptions change.

Feature-gated behavior means a test suite run without `rio-v2` does not exercise the MinIO S2 scheme, object-key APIs, sequence-number decryptors, or encrypted padding behavior.

## Test Signals

The local test module covers `WritePlan` passthrough, compression-then-encryption multipart round trip, and under `rio-v2`, singlepart and multipart object-key encryption round trips, S2 stream emission and seekable index availability for large compressed data, skipped indexes for smaller data, small compressed encrypt/decrypt round trip, encrypted S2 padding frame insertion and 256-byte alignment, and first-read behavior for v2 decompression on small and larger buffers.

The tests provide strong signal for write-pipeline ordering and rio-v2 compatibility behavior. The visible gaps are metadata parser tests for `compression_scheme_to_algorithm`, `compression_scheme_to_read_plan`, index decode fallback paths, and read helper selection across both feature configurations.
