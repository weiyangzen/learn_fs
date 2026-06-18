<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_linux_fallback_test.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_linux_fallback_test.go

- Purpose: Explicitly tests the Unix fallback tempfile path on Linux.
- Important APIs/types/functions: `TestCreateFallback`.
- Control flow: Calls `VerifyTempfile` with `createUnixFallback`.
- State and persistence: Uses a temporary file that is unlinked while open.
- Dependencies and integration points: Build-constrained to Linux; depends on package-local fallback function.
- Risks and edge cases: Does not force `O_TMPFILE` failure in `CreateAutoDelete`; it directly exercises the fallback helper.
- Test signals: Direct fallback coverage on Linux.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_linux_fallback_test.go -->
