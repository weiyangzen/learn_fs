# File Research: sources/os/linux/linux-stable/fs/ocfs2/quota.h

Purpose: declares OCFS2 quota in-memory structures, quota recovery structures, global/local quota helpers, quota I/O APIs, dquot lifecycle hooks, and exported VFS quota operations/format objects.

Read coverage: complete file read, 123 lines.

Key structures:
- `struct ocfs2_dquot` embeds a generic VFS `struct dquot` and adds local quota file offset, physical quota block, owning chunk, global use count, last globally synced space/inode usage, and a lockless-list node for deferred reference dropping.
- `struct ocfs2_recovery_chunk` records one local quota chunk requiring crashed-node recovery, with chunk number and bitmap of entries to replay.
- `struct ocfs2_quota_recovery` stores per-quota-type recovery chunk lists.
- `struct ocfs2_mem_dqinfo` stores per-quota-type runtime state: flags, chunk/block counts, chunk list, global quota inode, qinfo lock resource, cached global/local info buffers, qtree state, delayed sync work, and optional recovery information.
- `struct ocfs2_quota_chunk` tracks a local quota chunk number and header buffer.

Declared APIs:
- Recovery: `ocfs2_begin_quota_recovery()`, `ocfs2_finish_quota_recovery()`, `ocfs2_free_quota_recovery()`.
- Physical and logical quota I/O: `ocfs2_quota_read()`, `ocfs2_quota_write()`, `ocfs2_read_quota_phys_block()`, `ocfs2_validate_quota_block()`.
- Global quota state: `ocfs2_global_read_info()`, `ocfs2_global_write_info()`, `__ocfs2_sync_dquot()`, `ocfs2_sync_dquot()`, `ocfs2_global_release_dquot()`, `ocfs2_lock_global_qf()`, `ocfs2_unlock_global_qf()`.
- Local dquot lifecycle: `ocfs2_create_local_dquot()`, `ocfs2_local_release_dquot()`, `ocfs2_local_write_dquot()`, `ocfs2_drop_dquot_refs()`.
- Exports slab caches, qtree operations, `ocfs2_quota_operations`, and `ocfs2_quota_format`.

Dependencies:
- Includes Linux quota/qtree/list/slab types and OCFS2 core state.
- Implemented mainly by `quota_global.c` and `quota_local.c`, with recovery coordination from journal/recovery paths.

Risk and edge cases:
- Quota state spans local per-node files and global qtree records; callers must respect lock ordering and sync/recovery ownership from the implementation.
- Deferred dquot reference dropping exists because some contexts, such as downconvert paths, cannot safely perform final quota release work inline.
- `OCFS2_MAXQUOTAS` fixes support to user and group quotas.
