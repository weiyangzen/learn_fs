# File Research: sources/os/linux/linux/fs/gfs2/incore.h

## Scope

Central in-core GFS2 data model header. Defines runtime structures for glocks, holders, inodes, resource groups, quota data, transactions, journals, mount arguments, lockspace state, per-cpu lock stats, and the superblock-private `gfs2_sbd`.

## Major Structures

- Logging: `gfs2_log_header_host`, `gfs2_log_operations`, `gfs2_bufdata`, `gfs2_trans`, `gfs2_jdesc`, `gfs2_revoke_replay`.
- Allocation: `gfs2_bitmap`, `gfs2_rgrpd`, `gfs2_blkreserv`, `gfs2_alloc_parms`.
- Locking: `lm_lockname`, `gfs2_glock_operations`, `gfs2_holder`, `gfs2_glock`, `lm_lockstruct`, `gfs2_lkstats`, `gfs2_pcpu_lkstats`.
- Inode/file state: `gfs2_inode`, `gfs2_file`.
- Quota/statfs: `gfs2_qadata`, `gfs2_quota_data`, `gfs2_statfs_change_host`, `local_statfs_inode`.
- Mount/superblock: `gfs2_args`, `gfs2_tune`, `gfs2_sb_host`, `gfs2_sbd`.

## Important Flags And Helpers

- Buffer bits: `BH_Pinned`, `BH_Escaped`.
- DLM recovery flags: `DFL_BLOCK_LOCKS`, `DFL_NO_DLM_OPS`, `DFL_FIRST_MOUNT`, `DFL_MOUNT_DONE`, `DFL_DLM_RECOVERY`, and related flags.
- Glock flags: `GLF_LOCK`, instantiate/demote/dirty/LRU/reply/delete/cancel states.
- Inode flags: `GIF_QD_LOCKED`, `GIF_SW_PAGED`, `GIF_GLOP_PENDING`.
- Superblock flags include journal, withdraw, recovery, freeze, kill, and eviction states.
- Inline helpers: `GFS2_I()`, `GFS2_SB()`, `glock_sbd()`, `gfs2_aspace()`, lock-stat increments, and `gfs2_max_stuffed_size()`.

## Invariants

- `lm_lockname` is designed as an rhashtable key with no internal holes before the key length.
- `struct gfs2_inode` embeds `struct inode` first so `GFS2_I()` is a container cast.
- Glock operation flags determine whether a glock has an attached metadata address space or LVB.
- `gfs2_sbd` is the cross-subsystem anchor for lock state, journals, rgrps, quota, log state, workqueues, and debugfs.
