# File Research: sources/windows/dokany/sys/lock.c

Implements byte-range lock control, either in-kernel through FsRtl or forwarded to user mode when configured.

Key entry points:
- `DokanDispatchLock()` validates file context, locks the FCB, chooses kernel versus user-mode lock handling, and builds `LOCK_CONTEXT` for user-mode file lock mode.
- `DokanCommonLockControl()` handles normal kernel file locks with oplock coordination and `FsRtlProcessFileLock()`.
- `DokanCompleteLock()` completes user-mode lock requests with the returned status.

Core mechanics:
- Directories reject byte-range lock requests.
- In kernel-lock mode, Dokan checks whether the operation can interfere with oplocks, waits/breaks oplocks when needed, then calls `FsRtlProcessFileLock()`.
- After `FsRtlProcessFileLock()`, Dokan sets `DoNotComplete` because FsRtl owns IRP completion.
- In user-mode lock mode, the event includes byte offset, length, key, user context, and filename.
- `Length == NULL` is tolerated with logging.

Filesystem relevance:
- This file controls Windows byte-range locking semantics for Dokan filesystems and determines whether lock correctness is enforced by the kernel or delegated to the user-mode filesystem.

Notable risks:
- Oplock interaction is conditional on Windows version helper availability and allocation-size checks.
- User-mode file lock mode shifts correctness responsibility out of the kernel.
