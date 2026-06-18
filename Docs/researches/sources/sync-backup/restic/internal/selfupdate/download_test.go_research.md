<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_test.go -->
# sources/sync-backup/restic/internal/selfupdate/download_test.go

## Purpose
Tests archive extraction for self-update on zip input.

## Important APIs and Control Flow
`TestExtractToFileZip` creates an in-memory zip archive with one executable-like file, calls `extractToFile` twice, reads output bytes, and overwrites between runs to verify replacement. Control flow stays local and avoids network/GPG behavior.

## State, Persistence, Dependencies, and Integration
State is a temp directory and generated archive bytes. Dependencies are `archive/zip`, `bytes`, filesystem APIs, and shared test helpers.

## Risks and Test Signals
The test catches extraction and overwrite regressions but does not cover bz2 archives, signature/hash validation, or platform-specific binary removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_test.go -->
