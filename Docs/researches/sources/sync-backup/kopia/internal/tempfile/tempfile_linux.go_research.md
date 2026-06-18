<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_linux.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_linux.go

- Purpose: Creates Linux auto-deleting temporary files using `O_TMPFILE` when supported.
- Important APIs/types/functions: `permissions`, `CreateAutoDelete`.
- Control flow: Opens `os.TempDir()` with `O_RDWR|O_TMPFILE|O_CLOEXEC`; on supported fallback errors (`EISDIR`, `EOPNOTSUPP`, or nil invalid fd) it calls `createUnixFallback`; otherwise returns an `os.PathError`.
- State and persistence: Returns an unlinked anonymous file descriptor when possible; fallback creates then unlinks a named file.
- Dependencies and integration points: Uses `golang.org/x/sys/unix`, `syscall`, and `os`.
- Risks and edge cases: `O_TMPFILE` support varies by filesystem/kernel; fallback path must preserve delete-on-close semantics.
- Test signals: Covered by generic tempfile verification and `tempfile_linux_fallback_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_linux.go -->
