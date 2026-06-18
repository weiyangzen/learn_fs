# File Research: sources/os/linux/linux/fs/ocfs2/quota.h

Role: Declares OCFS2 quota in-memory structures, caches, and quota operation APIs for local and global quota handling.

Key contents:
- `OCFS2_MAXQUOTAS` is `2`, covering user and group quota types.
- `struct ocfs2_dquot` embeds the generic VFS `struct dquot` and adds:
  - local quota-file offset and physical block
  - containing quota chunk
  - global use count
  - last globally synced space/inode usage
  - lockless-list node for deferred dquot reference dropping
- `struct ocfs2_recovery_chunk` records a quota chunk number and bitmap for recovery.
- `struct ocfs2_quota_recovery` holds recovery chunk lists per quota type.
- `struct ocfs2_mem_dqinfo` stores quota header/runtime state:
  - quota type, flags, chunk/block counts, sync interval
  - chunk list
  - global quota inode and lock resource
  - buffer heads and holder counts for global/local quota inode/info blocks
  - qtree info, delayed sync work, and optional recovery state
- `OCFS2_DQUOT()` maps a generic `struct dquot` to `struct ocfs2_dquot`.
- `struct ocfs2_quota_chunk` tracks a local quota-file chunk and its header buffer.
- Declares slab caches `ocfs2_dquot_cachep` and `ocfs2_qf_chunk_cachep`.
- Declares global qtree format operations `ocfs2_global_ops`.
- Declares recovery APIs: begin, finish, free quota recovery.
- Declares quota file read/write and global info read/write.
- Declares dquot sync/release wrappers around `__ocfs2_sync_dquot()`.
- Declares global quota-file locking, quota block validation and physical block reads.
- Declares local dquot create/release/write and deferred dquot reference dropping.
- Exports VFS quota operations and quota format type.

Design notes:
- OCFS2 separates global quota accounting from per-node local quota deltas, then synchronizes through cluster locks and delayed work.
- The recovery structures mirror the need to replay or repair per-slot local quota changes after node failure.
