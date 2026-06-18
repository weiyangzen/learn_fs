# File Research: sources/os/linux/linux-stable/fs/f2fs/super.c

## Purpose
`super.c` is the F2FS superblock, mount, remount, module lifecycle, and filesystem-wide policy implementation. It wires F2FS into the VFS via `file_system_type`, `super_operations`, fscrypt, fsverity, export/NFS, quota, sysfs, shrinker, and mount option handling.

## Main Responsibilities
- Defines and parses all F2FS mount parameters through `fs_context` (`f2fs_parse_param`, `f2fs_context_ops`).
- Applies and validates mount options for GC, discard, quotas, compression, encryption, inline xattrs/data/dentries, checkpoint disable/merge, zoned devices, memory mode, error policy, lookup mode, NAT bits, and fault injection.
- Implements mount and remount flow through `f2fs_fill_super`, `f2fs_get_tree`, and `__f2fs_remount`.
- Reads, validates, repairs, and commits F2FS superblocks and checkpoints.
- Owns module initialization/exit ordering for all global F2FS caches and subsystems.
- Handles unmount teardown through `f2fs_put_super` and `kill_f2fs_super`.
- Implements quota integration, fscrypt callbacks, export operations, statfs, sync, freeze/unfreeze, shutdown, inode allocation/free/drop/dirty tracking, and critical error handling.

## Key Data and Interfaces
- `struct f2fs_fs_context` carries parsed mount options, changed option masks, spec masks, and quota-name changes before applying them to `struct f2fs_sb_info`.
- `f2fs_param_specs[]` defines the supported mount option grammar.
- `f2fs_sops` provides VFS superblock operations.
- `f2fs_cryptops` provides fscrypt integration when encryption is enabled.
- `f2fs_export_ops` enables file-handle based NFS export support.
- `f2fs_fs_type` registers the filesystem as `"f2fs"`.
- `f2fs_inode_cachep`, `f2fs_shrinker_info`, and the casefold slab are global resources created and destroyed at module load/unload.

## Mount Flow
`f2fs_fill_super` performs the full mount sequence:
1. Allocates `f2fs_sb_info`, initializes locks and inode lists.
2. Sets block size and reads both raw superblock copies.
3. Applies default and user-specified options, then validates consistency.
4. Sets VFS callbacks, flags, UUID, sysfs block-device name, and fscrypt/fsverity/xattr hooks.
5. Initializes write IO, `sbi` geometry, iostat, percpu counters, page-array cache, meta inode, checkpoint, devices, post-read workqueue, extent/ino/fsync tracking, checkpoint request control, segment manager, node manager, GC manager, stats, node inode, root inode, compression inode, and sysfs/procfs entries.
6. Enables quotas when needed, recovers orphan inodes and fsync data, resolves checkpoint-disabled state, starts background GC, joins the global shrinker, applies tuning, and announces the mounted checkpoint version.
7. Uses detailed unwind labels to destroy partially initialized state on failure.

## Validation and Recovery
- `sanity_check_raw_super` checks magic, checksum, block/sector geometry, segment counts, area boundaries, device layout, extension counts, checkpoint payload, and reserved inode numbers.
- `f2fs_sanity_check_ckpt` validates checkpoint metadata, current segment ranges, duplicate curseg usage, SIT/NAT bitmap sizes, NAT bits layout, and CP error state.
- `read_raw_super_block` accepts the first valid copy and marks recovery if either copy is bad.
- `f2fs_commit_super` writes backup then primary superblock, updating superblock CRC when appropriate.
- `f2fs_handle_error`, `f2fs_stop_checkpoint`, and `f2fs_handle_critical_error` record persistent error/stop reasons and enforce `errors=` policy.

## Remount and Checkpoint Policy
`__f2fs_remount` snapshots old mount options, validates new options, applies changes, manages RW/RO transition, quota suspend/resume, GC/flush/discard/checkpoint threads, checkpoint enable/disable, and restores old state on failure. Some options cannot be switched dynamically, including ATGC, extent caches, compression cache, discard unit class, and NAT bits.

`f2fs_disable_checkpoint` runs foreground GC until unusable blocks are under the configured cap, writes a pause checkpoint, and records disabled state. `f2fs_enable_checkpoint` flushes dirty/skipped data, moves dirty blocks to prefree, clears disabled state, and syncs.

## Quota Integration
With `CONFIG_QUOTA`, this file implements quota read/write, quota-on/off/sync, quota sysfile loading, project quota statfs limiting, dquot operations, and quotactl operations. It detects corrupted quota flags, marks repair-needed state, and handles quota recovery around orphan/fsync recovery.

## Dependencies
- Internal F2FS modules: `f2fs.h`, `node.h`, `segment.h`, `xattr.h`, `gc.h`, `iostat.h`.
- Closely coupled files in this group:
  - Uses `f2fs_xattr_handlers`, `f2fs_getxattr`, and `f2fs_setxattr` from `xattr.c`/`xattr.h`.
  - Installs `f2fs_verityops` from `verity.c` into `sb->s_vop`.
  - Calls `f2fs_init_sysfs`, `f2fs_register_sysfs`, and unregister/exit functions from `sysfs.c`.
- Kernel subsystems: VFS, fs_context, block layer, quota, fscrypt, fsverity, Unicode/casefolding, sysfs/procfs, shrinkers, workqueues, zoned block devices.

## Notable Edge Cases
- Zoned devices force discard and LFS-oriented constraints.
- Read-only hardware can allow mount only if no write recovery is required.
- `checkpoint=disable` is rejected on read-only mounts.
- Root-reserved block/node settings are capped to 12.5%.
- Casefold filesystems require `CONFIG_UNICODE`.
- Filesystems with readonly feature can only mount read-only.
- Superblock alignment may be fixed in memory and committed if writable.
