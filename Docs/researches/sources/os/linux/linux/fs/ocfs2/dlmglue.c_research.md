# File Research: sources/os/linux/linux/fs/ocfs2/dlmglue.c

OCFS2 DLM integration layer. This file turns generic cluster-stack DLM callbacks into OCFS2-specific lock resources, lock wrappers, lock value block handling, downconversion, debugfs inspection, and mount/unmount DLM lifecycle.

Major responsibilities:
- Defines per-lock-type operations through `struct ocfs2_lock_res_ops`.
- Initializes lock resources for inode metadata, inode rw/data, open, dentry, flock, quota info, refcount tree, superblock, rename, NFS sync, trim, and orphan-scan locks.
- Builds OCFS2 lock names from lock type, block number, and generation. Dentry locks use a special parent/name layout with embedded inode block number.
- Implements DLM AST, BAST, and unlock AST callbacks through the `ocfs2_locking_protocol`.
- Provides public lock wrappers used throughout OCFS2: inode locks, rw locks, open locks, flock locks, dentry locks, super/rename/NFS/trim/orphan-scan locks, quota info locks, and refcount locks.
- Runs the downconvert kernel thread that responds to other nodes’ blocking ASTs.

Lock state model:
- `struct ocfs2_lock_res` is guarded by `l_lock` and tracked in debug lists.
- Important flags include initialized, attached, busy, blocked, queued, pending, refreshing, upconvert-finishing, local, nocache, and freeing.
- Holder counts distinguish PR and EX holders.
- Mask waiters sleep until selected flag bits reach a goal state; with stats enabled, waits and lock timings are recorded.
- `OCFS2_LOCK_PENDING` plus `l_pending_gen` closes the race between setting `BUSY` and entering `ocfs2_dlm_lock()`, especially when an AST can fire before the DLM call returns.

DLM callback behavior:
- `ocfs2_blocking_ast()` records the requested incompatible level, marks the lock blocked, schedules it on the blocked list, wakes waiters, and wakes the downconvert thread.
- `ocfs2_locking_ast()` handles attach, convert, and downconvert completions, updates granted level, refresh-needed state, pending state, busy state, and waiters.
- `ocfs2_unlock_ast()` handles convert cancellation and final lock drop.
- DLM errors clear busy/upconvert state and wake waiters.

Core cluster lock path:
- `__ocfs2_cluster_lock()` handles attach, upconvert, wait, noqueue, nonblocking AOP retry behavior, holder accounting, LVB flags, and lockdep acquisition.
- `__ocfs2_cluster_unlock()` decrements holders and may wake the downconvert thread if a blocking request can now proceed.
- `ocfs2_lock_create()` attaches a new DLM resource.
- `ocfs2_downconvert_lock()` converts a held lock to the compatible level requested by a remote node.

LVB handling:
- Metadata LVBs cache inode size, clusters, uid/gid, mode, link count, packed atime/mtime/ctime, inode attributes, dynamic features, and generation.
- `ocfs2_inode_lock_update()` refreshes inode state after acquiring a meaningful metadata lock. It trusts the LVB only when valid, version-matched, and generation-matched; otherwise it purges metadata/extent caches and rereads the dinode.
- Deleted inodes invalidate their LVB by setting version 0.
- Quota info LVBs cache quota grace/sync and global-info block accounting.
- Orphan scan and trim locks use small LVBs for sequence/status transfer.

Public lock wrappers:
- `ocfs2_create_new_inode_locks()` creates local/exclusive locks for newly created inodes before other nodes can see them.
- `ocfs2_rw_lock()` / `ocfs2_rw_unlock()` protect cross-node data/rw operations.
- `ocfs2_open_lock()` and `ocfs2_try_open_lock()` coordinate open/exclusive-open style checks.
- `ocfs2_inode_lock_full_nested()` acquires metadata locks, waits for recovery when needed, refreshes inode state, and optionally returns a dinode buffer.
- `ocfs2_inode_lock_with_folio()` is a page/folio-lock inversion escape hatch for address-space operations; on `-EAGAIN` it unlocks the folio and asks VFS to retry.
- `ocfs2_inode_lock_tracker()` prevents recursive cluster-lock upgrades inside one task by tracking stack-local holders.
- `ocfs2_file_lock()` and `ocfs2_file_unlock()` implement flock-specific DLM locking with no caching and signal-driven cancel-convert support.
- Super, rename, NFS sync, trim, dentry, qinfo, orphan scan, and refcount helpers wrap `ocfs2_cluster_lock()` with type-specific refresh/LVB behavior.

Downconversion:
- Blocked locks are queued under `osb->dc_task_lock` and processed by `ocfs2_downconvert_thread()`.
- `ocfs2_unblock_lock()` refuses to downconvert while pending, busy, still held incompatibly, refreshing, or not checkpointed.
- Metadata and refcount locks require their caching info to be fully checkpointed before EX downconversion.
- Data/meta inode downconversion unmaps mappings, writes dirty pages, truncates pages for EX blockers, waits for I/O for PR blockers, increments directory lock generation, and drops cached ACLs.
- Dentry downconversion invalidates local dentries with `d_delete()`, handles final dentry-lock reference drops through post-unlock callbacks, and marks the inode maybe-orphaned.
- Refcount downconversion purges the refcount tree metadata cache.

Lifecycle and cleanup:
- `ocfs2_dlm_init()` starts the downconvert thread, connects to the cluster stack, negotiates locking protocol, discovers the local node number, and initializes OSB lock resources.
- `ocfs2_dlm_shutdown()` drops OSB locks, stops the downconvert thread, frees OSB lock resources, disconnects the cluster, and releases debug state.
- `ocfs2_simple_drop_lockres()` marks a lock resource freeing, waits for blocked-list removal, sets LVB if needed, and calls DLM unlock.
- `ocfs2_drop_inode_locks()` drops open, metadata, and rw locks during inode teardown.

Debug support:
- Tracks live lock resources in `ocfs2_dlm_debug`.
- Exposes debugfs `locking_state` and `locking_filter`.
- Sequence output includes lock name/type state, flags, holders, requested/blocking levels, raw LVB bytes, and optional timing/failure/refresh stats.

Important invariants and risks:
- Many paths depend on exact flag transitions under `l_lock`; missed pending or busy handling can deadlock cluster lock conversion.
- LVB writes are only safe when EX is held and refresh state is clean.
- Downconvert workers may sleep and must recheck lock level/blocking state afterward.
- The dentry downconvert path deliberately does dcache/iput-sensitive work in the downconvert thread and has special freeing logic to avoid self-deadlock.
- Lock tracker forbids PR-to-EX recursive upgrades because two-node upgrade cycles can deadlock.
