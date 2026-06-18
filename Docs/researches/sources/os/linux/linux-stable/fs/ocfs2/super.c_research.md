# File Research: sources/os/linux/linux-stable/fs/ocfs2/super.c

Implements OCFS2 module lifecycle, filesystem type registration, mount/remount parsing, superblock probing and initialization, mount/dismount orchestration, system inode loading, quota enable/disable, statfs, inode slab setup, debugfs state reporting, and filesystem error policy.

Key responsibilities:
- Registers the `ocfs2` filesystem type and quota format at module init.
- Initializes OCFS2 inode, dquot, quota-chunk, and uptodate-cache slabs.
- Parses mount options using `fs_context` parameter specs.
- Probes for OCFS2 superblocks across supported block sizes and rejects OCFS1 volumes.
- Builds `struct ocfs2_super`, VFS superblock operations, feature flags, cluster-stack metadata, workqueues, recovery state, journal object, slot info, and system inode caches.
- Mounts the clustered volume by initializing DLM, locking the superblock, selecting a slot, checking/recovering the volume, loading local alloc, and initializing truncate log.
- Completes mount recovery, quota recovery, and orphan scanning after root dentry setup.
- Dismounts in reverse order, stopping sysfs/debugfs, orphan scan, quota recovery, quotas, local allocator, truncate log, recovery, slots, system inodes, journal, DLM, and heartbeat hangup.

Important mount/remount behavior:
- `ocfs2_fill_super()` probes and initializes the superblock, applies options, validates userspace stack and heartbeat mode, handles hard-readonly devices, creates debugfs/sysfs state, mounts the volume, builds the root dentry, enables quotas if writable, and starts orphan scanning.
- `ocfs2_mount_volume()` skips cluster setup for hard-readonly mounts; otherwise it initializes DLM, takes super lock, finds a slot, loads local system inodes, checks/replays the volume, and initializes truncate log.
- `ocfs2_check_volume()` initializes and loads the journal, verifies journal addressability for large volumes, recovers local alloc after dirty mounts, loads local alloc, marks dead nodes, and computes replay slots.
- `ocfs2_reconfigure()` forbids changing heartbeat mode, data mode, and enabling `inode64` on remount; it manages RO/RW transitions and quota suspension/resume.
- `ocfs2_check_set_options()` validates heartbeat option exclusivity, quota feature availability, and ACL/xattr compatibility.

Important VFS/module hooks:
- `ocfs2_sops` provides `statfs`, inode allocation/freeing, eviction, sync, put_super, mount-option display, and quota file I/O hooks.
- `ocfs2_fs_type` uses `get_tree_bdev()` and `kill_block_super`.
- `ocfs2_sync_fs()` flushes the truncate log and starts/waits for JBD2 commits.
- `ocfs2_statfs()` reads the global bitmap system inode under lock and reports block/free/file counts.
- `ocfs2_alloc_inode()` and `ocfs2_inode_init_once()` initialize OCFS2 inode state, lock resources, extent map, metadata cache, reservations, and JBD2 inode linkage.

System inode and quota behavior:
- Global system inodes include root, system directory, and online/global system files; local system inodes are loaded after slot assignment.
- `ocfs2_need_system_inode()` skips quota system inodes when quota feature bits are absent.
- `ocfs2_enable_quotas()` loads local quota system inodes with `QFMT_OCFS2`.
- `ocfs2_disable_quotas()` cancels periodic sync work and disables loaded quotas.

Error behavior:
- `__ocfs2_error()` logs corruption and applies the mount `errors=` policy: panic, continue with `-EIO`, or remount read-only.
- `__ocfs2_abort()` is stronger and forces panic behavior for clustered mounts.
- `ocfs2_block_signals()`/`ocfs2_unblock_signals()` provide full signal masking helpers for in-kernel critical sections.

Risk areas:
- Mount/unmount failure labels must preserve ordering across DLM, journal, slot, local alloc, truncate log, quotas, sysfs/debugfs, and recovery state.
- Hard-readonly mounts intentionally skip cluster services and recovery; dirty journals require writable access.
- Remount RW must reject unsupported RO-compatible features and prior filesystem errors.
- Quota enablement is delayed until mount recovery can tolerate cluster-lock waits.
- Superblock feature parsing and cluster-stack validation must match on-disk metadata exactly.
