# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_lock.c

Purpose: implements byte-range locking for PVFS, including strict I/O lock checks, synchronous and timed async locks, unlocks, cancellation, close cleanup, and oplock release forwarding.

Important APIs and types: `pvfs_check_lock` tests I/O ranges when strict locking is enabled. `struct pvfs_pending_lock` tracks timed lock requests. Public operations are `pvfs_lock`, `pvfs_lock_close`, and internal helpers `pvfs_pending_lock_continue`, `pvfs_lock_async_failed`, and `pvfs_lock_cancel`.

Control flow: non-generic lock levels are mapped with `ntvfs_map_lock`. Generic lock dispatch handles oplock release, validates file handle and non-directory fd, breaks level-2 oplocks, creates pending state for nonzero timeouts when async is allowed, processes unlocks first, then attempts locks through `brlock_lock`. On immediate failure it rolls back acquired locks. For timed locks it registers a `pvfs_wait_message` for `MSG_BRL_RETRY` until retry, timeout, or cancel; continuation retries and either completes, requeues, or rolls back. Close removes all brlocks and replies to pending requests with range-not-locked.

State and persistence: lock state lives in Samba brlock context and per-file `lock_count`/`pending_list`. It is transient server coordination state, not persistent filesystem metadata.

Dependencies and integration points: uses brlock subsystem, messaging, wait helpers, NTVFS async state, PVFS file handles, and oplock break/release code.

Risks: rollback correctness is critical for multi-lock batches; cancel requires exact match; SMB1 and SMB2 cancellation statuses differ; pending lock lifetime is tied to file and wait handles; strict-locking off bypasses read/write lock checks. Test signals include lock/unlock ordering, failed-batch rollback, timed lock retry/timeout/cancel, close with active locks, directory lock rejection, shared/exclusive mapping, strict-lock I/O checks, and oplock release path.
