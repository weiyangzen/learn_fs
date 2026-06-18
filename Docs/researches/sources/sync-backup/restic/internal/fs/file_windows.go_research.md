# sources/sync-backup/restic/internal/fs/file_windows.go

Purpose: Windows path normalization, temp file creation, chmod passthrough, attribute clearing, and EA handle opening.

Important APIs: `fixpath`, `TempFile`, `chmod`, `clearSystem`, `clearAttribute`, and `openHandleForEA`.

Control flow and state: `fixpath` converts absolute paths to extended-length `\\?\` or `\\?\UNC\` paths, preserving VSS `GLOBALROOT` paths and appending a slash for bare snapshot volumes. `TempFile` uses `CreateFile` with temporary and delete-on-close flags and retries random suffix collisions. EA handles are opened with `FILE_READ_EA` and optional `FILE_WRITE_EA`.

Dependencies and integration: Used by almost all Windows filesystem operations, including security descriptor restore, EA restore, VSS path access, and long-path support.

Risks: Path-prefix handling must be exact; malformed `GLOBALROOT`, UNC, or volume GUID paths can break backup/restore. `TempFile` uses pseudo-random suffixes and a fixed retry count.

Test signals: `file_windows_test.go`, `node_windows_test.go`, and Windows EA/security tests validate temp deletion, long path/volume handling, and EA handle usage.
