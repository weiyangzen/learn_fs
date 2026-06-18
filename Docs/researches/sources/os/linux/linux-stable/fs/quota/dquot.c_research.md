# File Research: sources/os/linux/linux-stable/fs/quota/dquot.c

## Purpose
Implements the generic VFS disk quota core: dquot cache management, quota format registration, quota on/off, inode dquot attachment, quota accounting for block/inode allocation, quota ownership transfer, dirty writeback, user-visible quota state, and exported `dquot_operations` / `quotactl_ops`.

## Main Responsibilities
- Maintains global quota format registry via `register_quota_format`, `unregister_quota_format`, and module autoload in `find_quota_format`.
- Maintains dquot lifetime through hash table, `inuse_list`, `free_dquots`, `releasing_dquots`, dirty lists, slab cache, shrinker, and delayed release workqueue.
- Provides `dqget`, `dqgrab`, `dqput`, `dquot_acquire`, `dquot_commit`, `dquot_release`, and invalidation/writeback helpers.
- Attaches dquots to inodes using `i_dquot()` under `dq_data_lock` with `dquot_srcu` protection.
- Accounts allocation/freeing of blocks, reserved space, and inodes with limit enforcement and delayed warning emission.
- Implements transfer of usage between dquots for ownership changes.
- Implements quota enable/disable/resume and setup/cleanup of quota inode state.
- Exposes generic quota query/update operations for quota sysfile users.

## Key Concurrency Model
The file documents and enforces quota lock ordering:
- `dq_data_lock > dq_list_lock > inode->i_lock > dquot->dq_dqb_lock`
- `dq_list_lock > dq_state_lock`
- broader ordering: `s_umount > i_mutex > journal_lock > dquot->dq_lock > dqio_sem`

Important patterns:
- Inode dquot pointers are SRCU-protected.
- `DQ_RELEASING_B` prevents invalidation races during delayed release.
- `dquot->dq_lock` serializes disk read/write/release of an individual dquot.
- `dq_state_lock` protects quota on/off state transitions.

## Notable Functions
- `dqget()`: resolves or creates a cached active dquot for a `kqid`, waits for pending release, and acquires on-disk state as needed.
- `dqput()`: drops references and queues delayed release for last reference.
- `dquot_writeback_dquots()`: drains dirty dquot lists and writes quota metadata.
- `__dquot_initialize()`: attaches user, group, and project dquots to an inode.
- `__dquot_alloc_space()`, `dquot_alloc_inode()`, `__dquot_free_space()`, `dquot_free_inode()`: core accounting paths.
- `__dquot_transfer()` / `dquot_transfer()`: move usage when uid/gid ownership changes.
- `dquot_load_quota_inode()` / `dquot_load_quota_sb()`: turn quota accounting/enforcement on.
- `dquot_disable()` / `dquot_quota_off()`: suspend or turn quota off and invalidate cached dquots.
- `dquot_get_dqblk()`, `dquot_set_dqblk()`, `dquot_get_state()`, `dquot_set_dqinfo()`: generic user-facing quota operations.

## Interactions
Uses filesystem-supplied `quota_read`, `quota_write`, `dq_op`, and `s_qcop` hooks. Delegates on-disk format handling to registered quota format ops. Sends quota warnings through `quota_send_warning()` from `netlink.c`.

## Edge Cases
- Refuses quota files on encrypted inodes.
- Filesystems outside `init_user_ns` are not supported for VFS quota load.
- Handles quota file page-cache invalidation because quota I/O bypasses ordinary cached writes.
- Supports quota suspension separately from full quota disable.
- Root hardlimit bypass can be suppressed for old-format quotas with `DQF_ROOT_SQUASH`.
