<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/compress.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/compress.rs

## Purpose
Contains compression-only helpers for old log files. It intentionally separates archive creation from source deletion so a failed or partial compression cannot remove the original log.

## Important APIs, Types, and Functions
`CompressionOptions` carries algorithm, gzip/zstd levels, zstd worker count, fallback policy, and dry-run flag. `CompressionOutput` describes the archive path, codec used, input bytes, and output bytes. `compress_file` dispatches to gzip or zstd, with optional zstd-to-gzip fallback. Internal helpers include `compress_gzip`, `compress_zstd`, `compress_with_writer`, and `archive_path`.

## Control Flow
Compression first computes the target `<filename>.<ext>` archive path. If it already exists, the helper returns success metadata for idempotency. Dry-run returns planned output without creating files. Real compression writes to `archive.tmp`, flushes and finishes the encoder, optionally copies Unix permission bits, then atomically renames the temp file into place.

## State and Persistence
The persistent output is a `.gz` or `.zst` archive next to the source file. Incomplete temp archives are best-effort removed on writer failure. Source files are never deleted in this module.

## Dependencies and Integration
Uses `flate2` for gzip, `zstd` for zstd/zstdmt, std file I/O, and tracing. `cleaner::core` invokes it from serial and parallel cleanup paths.

## Risks
Existing archives are trusted as successful prior output even if corrupted or incomplete from an earlier external process. Atomic rename is local-filesystem safe but can fail across unusual mount behavior. Zstd multithreading may consume more CPU when many outer parallel workers are also active.

## Test Signals
No local tests are in this file, but cleaner integration tests exercise compression-enabled deletion paths indirectly where configured. Core metrics and log events expose compression success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/compress.rs -->
