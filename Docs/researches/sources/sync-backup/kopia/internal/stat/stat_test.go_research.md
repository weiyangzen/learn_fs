<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_test.go -->
# sources/sync-backup/kopia/internal/stat/stat_test.go

- Purpose: Tests stat helpers on non-Windows platforms.
- Important APIs/types/functions: `TestGetBlockSize`, `TestGetBlockSizeFromCurrentFS`, `TestGetFileAllocSize`.
- Control flow: Tests query block size for `os.DevNull` and current directory, then create a one-byte temp file and require allocated size to be at least 512 bytes.
- State and persistence: Uses temporary filesystem files only.
- Dependencies and integration points: Build-constrained to `!windows`; uses `os`, `filepath`, and `testify/require`.
- Risks and edge cases: Allocation minimum assumes conventional block accounting; exotic filesystems may behave differently.
- Test signals: Direct test coverage for Unix/BSD stat implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_test.go -->
