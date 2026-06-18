<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_test.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_test.go

- Purpose: Tests the public `tempfile.CreateAutoDelete` implementation selected for the current platform.
- Important APIs/types/functions: `TestTempFile`.
- Control flow: Delegates to `tempfile.VerifyTempfile`.
- State and persistence: Uses platform temporary files and close-time deletion.
- Dependencies and integration points: Imports package externally as `tempfile_test` to exercise public API.
- Risks and edge cases: Coverage is behavioral, not implementation-specific except through selected build tags.
- Test signals: Direct public API coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_test.go -->
