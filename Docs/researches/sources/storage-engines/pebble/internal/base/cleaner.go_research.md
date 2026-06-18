<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/cleaner.go -->
# sources/storage-engines/pebble/internal/base/cleaner.go

## Purpose
This file defines obsolete-file cleanup strategies for Pebble.

## Important APIs, Types, And Functions
`Cleaner` is the cleanup interface. `NeedsFileContents` marks cleaners requiring file contents. `DeleteCleaner` removes files. `ArchiveCleaner` moves log, manifest, table, and blob files into an `archive` directory and removes other file types.

## Control Flow
`DeleteCleaner.Clean` calls `fs.Remove`. `ArchiveCleaner.Clean` switches on `FileType`, creates an archive directory for persistent file types, renames the file there, or removes unsupported types.

## State And Persistence Behavior
This file directly affects filesystem state: deletion or rename into an archive sibling directory. `ArchiveCleaner` advertises that it needs file contents.

## Dependencies And Integration Points
It depends on `vfs.FS` and base `FileType`. Options and object storage cleanup code select a cleaner policy.

## Risks And Edge Cases
Archive behavior for secondary FS log files is noted as a TODO. Rename failures, directory creation failures, and platform-specific file semantics propagate as errors.

## Test Signals
Coverage is indirect through DB/file cleanup tests, including ingest cleanup and obsolete file handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/cleaner.go -->
