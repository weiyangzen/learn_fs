<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_unix_fallback.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_unix_fallback.go

- Purpose: Provides create-and-unlink fallback implementation for Unix-like platforms.
- Important APIs/types/functions: `createUnixFallback`.
- Control flow: Creates a temp file with prefix `kt-`, immediately removes the directory entry while keeping the handle open, closes on unlink failure, and returns the open file.
- State and persistence: File contents live only through the open descriptor; no path should remain after creation.
- Dependencies and integration points: Build-constrained to `linux || freebsd || darwin || openbsd`; uses `os` and `pkg/errors`.
- Risks and edge cases: If unlink fails, descriptor cleanup must happen to avoid leaks; returned `Name` can refer to a removed path.
- Test signals: Covered by generic tempfile tests and explicit Linux fallback test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_unix_fallback.go -->
