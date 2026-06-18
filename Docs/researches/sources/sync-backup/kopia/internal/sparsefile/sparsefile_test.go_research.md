<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/sparsefile/sparsefile_test.go -->
# sources/sync-backup/kopia/internal/sparsefile/sparsefile_test.go

- Purpose: Validates sparse copy output content against source files.
- Important APIs/types/functions: `TestSparseCopy`.
- Control flow: The test skips Windows, creates source/destination files, writes chunks at offsets, truncates destination, gets filesystem block size, runs `Copy`, then reads both files and compares bytes.
- State and persistence: Uses a temporary directory and filesystem sparse allocation behavior.
- Dependencies and integration points: Uses `stat.GetBlockSize`, `os`, `filepath`, `runtime`, and `testify/require`.
- Risks and edge cases: It verifies byte equality but does not assert physical allocation savings or short-reader buffer behavior.
- Test signals: Direct test coverage for `sparsefile.Copy`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/sparsefile/sparsefile_test.go -->
