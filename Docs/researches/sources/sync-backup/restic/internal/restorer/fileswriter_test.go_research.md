<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_test.go -->
# sources/sync-backup/restic/internal/restorer/fileswriter_test.go

## Purpose
Tests file creation, replacement, recursive deletion, hardlink safety, and writer cache behavior.

## Important APIs and Control Flow
`TestFilesWriterBasic` writes two files through a one-entry writer and verifies data after `flush`. `TestFilesWriterRecursiveOverwrite`, `TestCreateFile`, and `TestCreateFileRecursiveDelete` exercise regular files, empty/filled directories, symlinks, readonly files, hardlinks, sparse/non-sparse sizing, and recursive delete policy. Control flow creates target fixtures, invokes `writeToFile` or `createFile`, checks resulting file type/size/content, and cleans up.

## State, Persistence, Dependencies, and Integration
State is temporary filesystem data plus writer bucket/cache internals. Dependencies include `internal/fs`, `internal/errors`, syscall constants supplied by OS-specific test files, and shared test helpers.

## Risks and Test Signals
Coverage is strong for replacement edge cases. Remaining risks are high-contention concurrent write races and filesystem-specific preallocation/sparse behavior that unit tests may not fully expose.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_test.go -->
