<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/multiwriter.go -->
# sources/sync-backup/git-lfs/commands/multiwriter.go

Purpose: wraps an `io.MultiWriter` while preserving the original file descriptor, allowing command output writers to behave like files for consumers that need `Fd`.

Important APIs/types/functions: `multiWriter`, `newMultiWriter`, `Write`, and `Fd`.

Control flow: constructor prepends the provided `*os.File` to additional writers, stores the file descriptor, and `Write` delegates to the multiwriter. `Fd` returns the stored descriptor.

State and persistence behavior: writes are duplicated to the file and additional writers such as `ErrorBuffer`; the fd is captured at construction.

Dependencies/integration points: used by `ErrorWriter` and `OutputWriter` in `commands.go` to mirror stdout/stderr into panic logs while retaining file descriptor compatibility.

Risks and test signals: risks include stale fd if the underlying file is closed/replaced, partial write semantics from `io.MultiWriter`, and no synchronization. Test signals include duplicated writes to buffer and file, `Fd` matching original stdout/stderr, and error propagation from secondary writers.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/multiwriter.go -->
