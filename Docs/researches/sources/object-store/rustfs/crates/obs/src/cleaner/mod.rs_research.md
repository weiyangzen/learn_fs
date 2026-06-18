<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/mod.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/mod.rs

## Purpose
Defines the cleaner subsystem module boundary and documents the cleanup lifecycle. It re-exports the public `LogCleaner` API while keeping scanner/compressor/core internals organized.

## Important APIs, Types, and Functions
Declares private `compress`, `core`, and `scanner` modules plus public `types`. Re-exports `core::LogCleaner`. The module-level documentation explains scan, selection, compression, deletion, and archive expiration stages.

## Control Flow
No production control flow is implemented here beyond module wiring. The embedded tests construct cleaners and call cleanup behavior in integration-style scenarios.

## State and Persistence
No module-level state exists. Tests create temporary directories and files to validate filesystem effects.

## Dependencies and Integration
This file is the public entry point for observability log cleanup. Callers can import `rustfs_obs::LogCleaner` after crate-level re-export. Tests use `tempfile`, std file I/O, and `scanner::scan_log_directory`.

## Risks
The documentation says the cleaner preserves a minimum number of files, while tests and core behavior enforce `keep_files` as a ceiling on retained files. That semantic mismatch should be clarified for operators.

## Test Signals
Tests validate size-based cleanup, count-based cleanup, unrelated-file isolation, scanner matching, dry-run behavior, and suffix matching. They provide useful regression coverage for retention semantics and file selection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/mod.rs -->
