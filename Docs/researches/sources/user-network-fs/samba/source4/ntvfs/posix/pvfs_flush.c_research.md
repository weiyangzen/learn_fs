# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_flush.c

Purpose: implements SMB flush semantics for PVFS open files, optionally syncing file descriptors to disk when strict sync is enabled.

Important APIs and functions: `pvfs_flush_file` calls `fsync` on a file handle if it has a real fd and `PVFS_FLAG_STRICT_SYNC` is set. `pvfs_flush` handles `RAW_FLUSH_FLUSH`, `RAW_FLUSH_SMB2`, and `RAW_FLUSH_ALL`.

Control flow: single-file flush resolves the NTVFS handle with `pvfs_find_fd`, rejects invalid handles, calls `pvfs_flush_file`, initializes SMB2 reserved output, and returns OK. Flush-all returns OK immediately unless strict sync is enabled; when enabled it iterates all open PVFS files and flushes those whose stored SMB PID matches the request.

State and persistence: no state is stored. With strict sync, dirty kernel state may be persisted to disk via `fsync`. Without strict sync, flush is effectively acknowledged without forcing storage.

Dependencies and integration points: depends on PVFS file tracking and share flags. Used by NTVFS flush dispatch for SMB1/SMB2 callers.

Risks: `fsync` errors are ignored; directories or non-fd handles are skipped by `pvfs_flush_file`; flush-all filters by SMB PID rather than session. Test signals include invalid handle, SMB2 reserved output, strict-sync off no-op, strict-sync on `fsync` invocation, and flush-all PID filtering.
