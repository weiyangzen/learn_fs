# sources/storage-engines/pebble/internal/base/filenames_test.go

Purpose: Validates canonical filename construction, parsing, and missing-file error detail behavior.

APIs and types: Exercises `MakeFilename`, `MakeFilepath`, `ParseFilename`, `ParseDiskFileNum`, `FileTypeFromName`, and `AddDetailsToNotExistError`/`MustExist` related diagnostics.

Control flow and state: Table-driven cases verify known file names and invalid strings. Tests use VFS paths to ensure basename behavior and count directory contents for detail messages.

Persistence and dependencies: Uses test filesystem state to populate directories with recognized and unknown file names; no durable repository state is changed.

Integration points: Protects compatibility of filename formats consumed by DB open, manifest discovery, object storage, and cleanup code.

Risks: Tests are focused on naming grammar and diagnostics, not every object-storage lifecycle path. WAL filename specifics are intentionally outside this package.

Test signals: Strong table-driven coverage for edge cases around parsing and file-number conversion.
