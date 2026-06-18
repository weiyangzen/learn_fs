# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmglue.c

Purpose: Implements OCFS2's filesystem-specific interface to the cluster DLM, including lock-resource initialization, lock acquisition/release, lock value block handling, blocked-lock downconversion, and debugfs lock-state reporting.

Read coverage: complete file read, 4468 lines.

Key structures and state:
- `struct ocfs2_lock_res_ops` defines per-lock-type behavior: owner lookup, post-unlock cleanup, downconvert safety checks, LVB population, pre-downconvert worker, and lock-type flags.
- Lock operation tables cover inode RW locks, inode metadata locks, superblock, rename, NFS sync, trim, orphan scan, dentry, open, flock, quota info, and refcount-block locks.
- `struct ocfs2_mask_waiter` waits for specific `l_flags` transitions and optionally records lock timing stats.
- Lock resources track current/requested/blocking DLM levels, holders, pending DLM operations, blocked-list membership, waiters, and debug tracking.
- LVB formats handled here include inode metadata, quota info, orphan scan sequence, and trimfs result data.

Major logic:
- Builds stable OCFS2 lock names and initializes lock resources for inodes, dentries, file-private flock locks, quota info, refcount trees, and global mount locks.
- Implements DLM AST, BAST, and unlock-AST callbacks, translating DLM events into OCFS2 lock-resource state transitions.
- Provides `ocfs2_cluster_lock()` and `ocfs2_cluster_unlock()` as the generic lock acquire/release path with support for convert, attach, noqueue, nonblocking retry, waiters, LVB use, and lockdep.
- Uses `OCFS2_LOCK_PENDING` plus `l_pending_gen` to close the race between marking a lock busy and actually calling into the DLM.
- Refreshes stale inode state from metadata LVBs when trusted, otherwise purges metadata/extent caches and rereads the dinode from disk.
- Handles metadata LVB packing/unpacking for size, clusters, ownership, mode, link count, times, flags, dynamic features, and generation.
- Implements public wrappers for inode metadata locks, inode RW locks, open locks, flock locks, super locks, rename locks, NFS sync locks, trim locks, dentry locks, quota-info locks, orphan-scan locks, and refcount-tree locks.
- Maintains a downconvert kernel thread that processes blocked locks, calls type-specific workers, writes LVBs when safe, cancels conflicting converts, and requeues work when holders or checkpointing prevent downconversion.
- Supplies debugfs `locking_state` and `locking_filter` support with seq_file iteration over tracked lock resources and raw LVB/stat dumps.

Important entry points:
- Initialization and shutdown: `ocfs2_set_locking_protocol()`, `ocfs2_dlm_init()`, `ocfs2_dlm_shutdown()`.
- Lock-resource lifecycle: `ocfs2_lock_res_init_once()`, `ocfs2_inode_lock_res_init()`, `ocfs2_dentry_lock_res_init()`, `ocfs2_file_lock_res_init()`, `ocfs2_qinfo_lock_res_init()`, `ocfs2_refcount_lock_res_init()`, `ocfs2_lock_res_free()`.
- Inode locks: `ocfs2_inode_lock_full_nested()`, `ocfs2_inode_lock_with_folio()`, `ocfs2_inode_lock_atime()`, `ocfs2_inode_unlock()`, tracker variants.
- Other lock wrappers: `ocfs2_rw_lock()`, `ocfs2_try_rw_lock()`, `ocfs2_open_lock()`, `ocfs2_file_lock()`, `ocfs2_super_lock()`, `ocfs2_rename_lock()`, `ocfs2_nfs_sync_lock()`, `ocfs2_trim_fs_lock()`, `ocfs2_dentry_lock()`, `ocfs2_qinfo_lock()`, `ocfs2_refcount_lock()`.
- Cleanup and downconversion: `ocfs2_mark_lockres_freeing()`, `ocfs2_simple_drop_lockres()`, `ocfs2_drop_inode_locks()`, `ocfs2_wake_downconvert_thread()`.

Concurrency and lifetime:
- `l_lock` protects lock-resource state, holder counts, waiter lists, and pending action fields.
- `dc_task_lock` protects the mount's blocked-lock list and downconvert wake sequence.
- The downconvert path may run type-specific filesystem work without `l_lock`, then revalidates blocking state before issuing DLM converts.
- Metadata downconversion is gated by checkpoint completion so dirty metadata is not exposed incorrectly to other nodes.
- Dentry downconversion takes extra dentry-lock references to avoid final-reference teardown while invalidating aliases.
- Flock locks deliberately avoid caching and use signal-aware convert cancellation because userspace can self-deadlock.
- Debug tracking uses a global spinlock and copies lock resources before printing because the owning object may disappear after unlock.

Important dependencies:
- DLM stack glue, heartbeat node-down callbacks, journal checkpointing, metadata cache purge/checkpoint APIs, inode refresh, extent-map truncation, quota read/write helpers, dcache/dentry lock helpers, refcount-tree caching, ACL cache invalidation, and debugfs/seq_file infrastructure.
- Uses DLM LVBs and DLM convert/cancel/drop semantics through `ocfs2_dlm_lock()` and `ocfs2_dlm_unlock()`.

Risk and edge cases:
- Lock state transitions are race-sensitive; `OCFS2_LOCK_PENDING`, `OCFS2_LOCK_BUSY`, `OCFS2_LOCK_UPCONVERT_FINISHING`, and queued/freeing flags must remain synchronized.
- LVB metadata is trusted only when valid, versioned, and generation-matched; stale LVB use would corrupt in-memory inode state.
- Downconvert workers can sleep and can trigger dcache/inode teardown, so queue ownership and post-unlock callbacks are delicate.
- Local mounts and hard-readonly mounts bypass parts of cluster locking; wrapper semantics must preserve expected error behavior such as `-EROFS`.
- `ocfs2_inode_lock_with_folio()` intentionally returns `AOP_TRUNCATED_PAGE` on nonblocking lock conflict to break folio-lock/DLM-lock inversion.
- Lock resource freeing asserts no waiters, holders, busy state, or blocked-list membership; cleanup ordering violations become hard failures.
