<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_verify_test.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_verify_test.go

- Purpose: Provides shared tempfile behavior assertions for platform implementations.
- Important APIs/types/functions: `VerifyTempfile`.
- Control flow: Creates a file, writes `hello`, seeks, reads `ello`, closes, and if the file has a name, verifies `os.Stat` fails with platform-appropriate not-found text.
- State and persistence: Uses a single temporary file descriptor from the provided factory.
- Dependencies and integration points: Uses `io`, `os`, `runtime`, `testing`, and `testify/require`.
- Risks and edge cases: Error message text is platform-specific and can vary by Go/OS localization.
- Test signals: Shared direct coverage for public and fallback tempfile creators.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_verify_test.go -->
