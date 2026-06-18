<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_windows.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_windows.go

- Purpose: Creates Windows temporary files that are deleted automatically on close.
- Important APIs/types/functions: `CreateAutoDelete`.
- Control flow: Builds a random path under `os.TempDir`, converts to UTF-16, calls `syscall.CreateFile` with read/write access and `FILE_FLAG_DELETE_ON_CLOSE`, and wraps the handle as `*os.File`.
- State and persistence: The filesystem entry is scheduled for deletion by Windows handle semantics.
- Dependencies and integration points: Build-constrained to Windows; uses `google/uuid`, `x/sys/windows`, `syscall`, and `os`.
- Risks and edge cases: Sharing mode is zero, so concurrent access is intentionally restricted; path conversion and handle ownership must be correct.
- Test signals: Generic tempfile public API test covers behavior on Windows.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_windows.go -->
