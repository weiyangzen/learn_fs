<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/types.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/types.rs

## Purpose
Defines lightweight shared types for the cleaner pipeline: file matching modes, compression algorithms, default worker count, and discovered file metadata.

## Important APIs, Types, and Functions
`FileMatchMode` supports prefix and suffix matching, with parsing from config strings and display. `CompressionAlgorithm` supports gzip and zstd, accepts full names and extension aliases, reports archive extensions and compressed suffixes, and implements `FromStr`, `Default`, and display. `default_parallel_workers` clamps CPU count into 4..=8. `FileInfo` carries path, size, and modified timestamp.

## Control Flow
Parsing is permissive for config (`from_config_str` falls back to defaults) and strict for `FromStr` (invalid values error). Archive suffix helpers centralize `.gz` and `.zst` recognition.

## State and Persistence
No mutable state. `FileInfo` is a metadata snapshot used by later cleanup stages.

## Dependencies and Integration
Uses observability constants from `rustfs_config`, `num_cpus`, std formatting, paths, and time. Scanner, compressor, and core all depend on these types.

## Risks
Permissive config parsing can hide typos by silently falling back to defaults. The worker clamp uses at least four workers even on small machines, which improves concurrency tests but may be aggressive in constrained deployments.

## Test Signals
Tests validate compression algorithm parsing for names and aliases, fallback behavior for config parsing, and strict `FromStr` rejection of invalid values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/types.rs -->
