<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/scanner.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/scanner.rs

## Purpose
Scans a log directory once and classifies matching files as regular logs or already-compressed archives. It is the cleaner pipeline's first safety boundary.

## Important APIs, Types, and Functions
`LogScanResult` contains `logs` and `compressed_archives`. `scan_log_directory` takes directory, pattern, active filename, match mode, glob exclusions, minimum age, empty-file deletion, and dry-run flags. `is_excluded` checks filenames against compiled glob patterns.

## Control Flow
The scanner performs a shallow `read_dir` pass. Missing directories produce an empty result. It uses `symlink_metadata` so symlinks are not followed, skips non-regular files, skips the active log file, applies exclusions, recognizes compressed suffixes, strips archive suffixes for logical matching, optionally deletes empty regular logs, applies age gating to regular logs only, then appends `FileInfo` to the appropriate vector.

## State and Persistence
Normally read-only, but it can delete zero-byte regular log files during scan when enabled. In dry-run mode it logs intent instead. It returns metadata snapshots with size and modified time.

## Dependencies and Integration
Uses std filesystem APIs, `glob::Pattern`, tracing, and `CompressionAlgorithm::compressed_suffixes`. `core::cleanup` consumes its scan result for retention selection.

## Risks
The scan is non-recursive, so nested log layouts are ignored. Empty-file deletion happens before the main cleanup metrics counters in `core`, so separate accounting may be needed if operators care. Files can change after metadata snapshot, creating normal filesystem race conditions mitigated later by secure deletion.

## Test Signals
Tests in `cleaner::mod` validate scanner matching and ignoring unrelated files. Comments explicitly call out symlink safety and avoiding TOCTOU from metadata calls.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/scanner.rs -->
