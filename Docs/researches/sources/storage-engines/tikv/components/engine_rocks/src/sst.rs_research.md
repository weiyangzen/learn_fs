<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/sst.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/sst.rs

## Purpose
`sst.rs` implements the external SST reader/writer interfaces for `RocksEngine`. It supports opening SSTs with TiKV's encrypted/rate-limited environment, iterating and checksumming SST contents, building disk or in-memory SST files, selecting compression, and exposing `ExternalSstFileInfo`.

## Important APIs, Types, and Functions
`RocksSstReader` wraps `rocksdb::SstFileReader`; `open_with_env`, `compression_name`, `verify_checksum`, `kv_count_and_size`, and `RefIterable::iter` are the key APIs. `RocksSstIterator` adapts `DBIterator<&SstFileReader>` to `engine_traits::Iterator`.

`RocksSstWriterBuilder` implements `SstWriterBuilder<RocksEngine>` with setters for DB, CF, in-memory mode, compression type, and compression level. `build` derives CF options from a DB when present, swaps in a memory env when requested, validates requested compression against `supported_compression`, forces compression settings for SST writer use, and opens a `SstFileWriter`.

`RocksSstWriter` implements `SstWriter`. `finish` returns `RocksExternalSstFileInfo`; `finish_read` also opens a resettable sequential file through the writer env. `ResettableSequentualFile` implements both `Read` and `ExternalSstFileReader::reset`. Compression helpers convert between `SstCompressionType` and RocksDB `DBCompressionType`.

## Control Flow
Reader `open` builds an env from `get_env(DataKeyManager, get_io_rate_limiter())`, opens the SST reader, and defers table-property access to closures. Writer `build` chooses CF options from the configured DB/CF or defaults, installs an env, chooses explicit or fastest-supported compression, applies compression-level options when nonzero, disables per-level and bottommost compression overrides, opens the writer, and returns it with the env needed for later reading.

Iterator methods validate before `next`/`prev` unless `nortcheck` is enabled, then forward to RocksDB. `finish_read` requires that `env` is present, finishes the writer, converts the file path to UTF-8, and opens a new sequential file that can be reset by reopening the path.

## State and Persistence Behavior
Disk-backed writers create actual SST files at the requested path. In-memory writers use `Env::new_mem` and can return a readable sequential file without a disk artifact. `finish` consumes the writer, finalizing the SST. The reader is read-only and verifies checksums or table metadata from the file.

## Dependencies and Integration Points
It depends on RocksDB SST APIs, `engine_traits::{SstExt, SstReader, SstWriter, SstWriterBuilder, ExternalSstFileInfo}`, encryption env construction, file-system rate limiting, and failpoint `on_open_sst_writer`. Import/ingest paths use these abstractions to create, inspect, and stream SSTs.

## Risks and Edge Cases
`finish_read` fails when no env is available, so builder state must keep an env for memory or DB-backed writes. Compression support is runtime-dependent; unsupported explicit compression returns an error. Compression level `0` is treated as "do not set options" even though RocksDB may consider zero valid. Path conversion requires valid UTF-8. Iterator `key`/`value` assume a valid iterator position.

## Test Signals
`test_smoke` writes a disk SST, checks metadata and disk existence, then writes an in-memory SST, reads it through `finish_read`, resets the reader, and verifies no disk file exists. Further tests should cover unsupported compression, checksum failure, explicit compression levels, CF option inheritance, and encrypted env behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/sst.rs -->
