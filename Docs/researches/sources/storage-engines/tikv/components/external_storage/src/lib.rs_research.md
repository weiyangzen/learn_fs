<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/lib.rs -->
# sources/storage-engines/tikv/components/external_storage/src/lib.rs

Purpose: this is the root of the `external_storage` crate. It defines the `ExternalStorage` trait, common restore/read helpers, encryption/compression/checksum plumbing, backend config structs, and public module exports.

Important APIs and types: `ExternalStorage` requires `name`, `url`, async `write`, `read`, `read_part`, `iter_prefix`, and `delete`; it also provides a default async `restore`. `UnpinReader` erases reader types for async trait signatures. `BackendConfig` carries S3 multipart size, GCP v2 selection, and HDFS config. `RestoreConfig` carries range, compression type, expected plaintext checksum, file encryption info, and optional encrypted checksum. Helpers include `compression_reader_dispatcher`, `encrypt_wrap_reader`, `read_external_storage_into_file`, `read_external_storage_info_buff`, and `wrap_with_checksum_reader_if_needed`.

Control flow: default `restore` chooses full or ranged read, optionally wraps a SHA-256 reader around encrypted bytes, optionally decrypts, dispatches compression (unknown means uncompressed, zstd gets a decoder), creates the local output through `file_system::File`, and copies through `read_external_storage_into_file`. That copy loop applies per-read timeout based on a minimum speed, consumes a `Limiter`, writes to output, optionally hashes plaintext, yields periodically, validates expected length, validates encrypted checksum, and validates plaintext checksum.

State and persistence behavior: restore persists a local file. Checksum state is held in OpenSSL `Hasher` instances, including a shared hasher behind `Arc<Mutex<Hasher>>` for encrypted-byte streaming. No backend registry state is maintained.

Dependencies and integration points: the root exports `LocalStorage`, `HdfsStorage`, `NoopStorage`, `IterableStorage`, locking, metrics, and all exports from `export.rs`. It integrates `async-compression`, `encryption`, `file_system`, `kvproto`, `openssl`, `tikv_util::Limiter`, and Tokio timeout/yielding.

Risks: `calc_and_compare_checksums` calls `finish` while holding a mutex guard; callers must treat the hasher as consumed after validation. Default restore creates the output file before validating final checksums, so failed validation can leave a partial or invalid local file. `CompressionType::Unknown` is treated as uncompressed for compatibility with old log files, which is intentional but easy to misread.

Test signals: tests for helper functions are not in this file excerpt, but downstream tests in backend modules and compile-time trait implementations cover major paths. The key behavioral risk areas are timeout behavior, partial output cleanup, and checksum ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/lib.rs -->
