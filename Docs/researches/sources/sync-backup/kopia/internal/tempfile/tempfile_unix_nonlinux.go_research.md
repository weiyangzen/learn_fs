<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_unix_nonlinux.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_unix_nonlinux.go

- Purpose: Selects the Unix fallback implementation as the public auto-delete tempfile implementation on FreeBSD, Darwin, and OpenBSD.
- Important APIs/types/functions: `CreateAutoDelete`.
- Control flow: Immediately delegates to `createUnixFallback`.
- State and persistence: Same create-and-unlink descriptor behavior as the fallback helper.
- Dependencies and integration points: Build-constrained to `freebsd || darwin || openbsd`; imports `os` for signature.
- Risks and edge cases: Lacks Linux `O_TMPFILE` optimization but should preserve deletion behavior.
- Test signals: Generic tempfile tests cover this path on matching platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_unix_nonlinux.go -->
