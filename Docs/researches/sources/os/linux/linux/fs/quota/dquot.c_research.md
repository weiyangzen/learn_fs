# File Research: sources/os/linux/linux/fs/quota/dquot.c

Core VFS disk-quota implementation. This file owns generic `struct dquot` lifecycle, quota accounting, dirty/writeback paths, quota-on/off state transitions, and the default `dquot_operations` / `quotactl_ops` exported to filesystems.

Key responsibilities:
- Registers and unregisters quota formats via `register_quota_format()` / `unregister_quota_format()`, including lazy module loading in `find_quota_format()`.
- Maintains global dquot lists and hash table: `inuse_list`, `free_dquots`, `releasing_dquots`, per-info dirty lists, and `dquot_hash`.
- Implements dquot reference management through `dqget()`, `dqgrab()`, and `dqput()`.
- Uses delayed work plus `synchronize_srcu(&dquot_srcu)` in `quota_release_workfn()` so inode-held dquot pointers can be cleared safely before final release.
- Implements read/commit/release of dquots with `dquot_acquire()`, `dquot_commit()`, `dquot_release()`, and writeback with `dquot_writeback_dquots()` / `dquot_quota_sync()`.
- Handles inode quota pointer initialization/drop through `__dquot_initialize()`, `dquot_initialize()`, `dquot_drop()`, `add_dquot_ref()`, and `remove_dquot_ref()`.
- Performs quota accounting for blocks, reserved space, and inodes via `__dquot_alloc_space()`, `dquot_alloc_inode()`, `dquot_claim_space_nodirty()`, `dquot_reclaim_space_nodirty()`, `__dquot_free_space()`, and `dquot_free_inode()`.
- Transfers quota usage during ownership changes via `dquot_transfer()` and `__dquot_transfer()`.
- Enables, disables, suspends, resumes, and mounts quota files through `dquot_disable()`, `dquot_quota_off()`, `dquot_load_quota_sb()`, `dquot_load_quota_inode()`, `dquot_resume()`, `dquot_quota_on()`, and `dquot_quota_on_mount()`.
- Implements generic get/set quota state and limits: `dquot_get_dqblk()`, `dquot_get_next_dqblk()`, `dquot_set_dqblk()`, `dquot_get_state()`, and `dquot_set_dqinfo()`.
- Exposes `/proc/sys/fs/quota/*` counters via `fs_dqstats_table`.

Important synchronization:
- Documented spinlock order is `dq_data_lock > dq_list_lock > i_lock > dquot->dq_dqb_lock`, with `dq_list_lock > dq_state_lock`.
- `dq_data_lock` protects inode dquot pointer updates and `mem_dqinfo`.
- `dq_state_lock` protects quota loaded/enforced/suspended state.
- `dq_list_lock` protects global dquot lists, format list, and hash table.
- `dquot->dq_lock` serializes on-disk read/write/release for a single dquot.
- `dquot_srcu` protects readers of inode dquot pointers while quotaoff clears references.

Notable behavior:
- Quota warnings are prepared inside accounting sections but flushed afterward, avoiding calls into tty or netlink while holding low-level quota locks.
- `ignore_hardlimit()` lets privileged callers bypass hard limits except when old-format root squash forbids it.
- Quota files are marked `S_NOQUOTA` and stripped of dquot references to avoid recursive quota accounting and deadlocks.
- External quota file enablement flushes and invalidates page/buffer cache so direct quota IO observes user changes.
- `DQUOT_QUOTA_SYS_FILE` supports filesystems with hidden quota metadata, where quotactl can enable or disable enforcement but not accounting.
- The shrinker reclaims clean free dquots from `free_dquots`.

Interfaces exported:
- Format registration: `register_quota_format`, `unregister_quota_format`.
- Dquot lifecycle/accounting: `dqget`, `dqput`, `dqgrab`, `dquot_initialize`, `dquot_drop`, allocation/free/transfer helpers.
- Quota operations: `dquot_operations`, `dquot_quotactl_sysfile_ops`.
- Quota file control: `dquot_quota_on`, `dquot_quota_off`, `dquot_quota_on_mount`, `dquot_resume`.

Research notes:
- This is the central quota engine; `quota.c` is the user ABI dispatcher, while `quota_v1.c`, `quota_v2.c`, and `quota_tree.c` provide backing formats.
- The file is sensitive to lock ordering, SRCU lifetime, and memory reclaim recursion; most quota IO paths use `memalloc_nofs_save()`.
