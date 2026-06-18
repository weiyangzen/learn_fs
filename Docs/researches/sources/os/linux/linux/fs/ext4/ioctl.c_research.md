# File Research: sources/os/linux/linux/fs/ext4/ioctl.c

## Purpose

`ioctl.c` implements ext4's ioctl and file attribute control plane. It exposes administrative operations for inode generation numbers, flags, project IDs, online resize, extent migration/move, delayed allocation flushing, boot-loader inode swapping, filesystem trim, encryption and verity ioctls, extent status cache inspection, forced shutdown, journal checkpointing, filesystem label/UUID updates, online superblock tuning, and overhead-cluster persistence.

## Main Entry Points

- `ext4_ioctl()` forwards all native ioctl handling into `__ext4_ioctl()`.
- `ext4_compat_ioctl()` maps selected 32-bit compat ioctl command numbers and argument layouts to the native implementation.
- `ext4_fileattr_get()` and `ext4_fileattr_set()` implement VFS file-attribute integration for ext4 flags and project IDs.
- `ext4_force_shutdown()` performs the forced shutdown operation used by `EXT4_IOC_SHUTDOWN`.
- `ext4_update_overhead()` persists recalculated filesystem overhead cluster counts through the shared superblock update helper.
- `ext4_reset_inode_seed()` recomputes per-inode metadata checksum seeds after inode generation changes.

## Superblock Update Helpers

- `ext4_update_primary_sb()` journals and synchronously writes the primary superblock after invoking a caller-supplied callback.
- `ext4_update_backup_sb()` updates backup superblocks, optionally under a journal handle, and validates metadata checksums before modifying checksum-protected backups.
- `ext4_update_superblocks_fn()` serializes against online resize with `EXT4_FLAGS_RESIZING`, journals the primary superblock and at most two backups, then updates remaining backups without journaling.
- Callback helpers include:
  - `ext4_sb_setlabel()` for `s_volume_name`.
  - `ext4_sb_setuuid()` for `s_uuid`.
  - `ext4_sb_setparams()` for online tune parameters.
  - `set_overhead()` for `s_overhead_clusters`.

These helpers centralize checksum recalculation, buffer locking, dirty metadata handling, writeback, and backup-superblock iteration for ioctl paths that mutate superblock fields.

## Inode Data Swapping

- `memswap()` provides a bytewise swap utility.
- `swap_inode_data()` swaps `i_data`, selected ext4 flags, disk size, VFS size, timestamps, version, and extent status cache state between two inodes.
- `swap_inode_boot_loader()` implements `EXT4_IOC_SWAP_BOOT` by swapping a regular user file with `EXT4_BOOT_LOADER_INO`.

The boot-loader swap path performs strong validation before modifying metadata: the source must be a single-link regular file, not a swapfile, encrypted file, journal-data file, or inline-data file. It requires ownership/capability checks, `CAP_SYS_ADMIN`, write access, page writeback completion, DIO quiescence, page-cache truncation, a journal transaction, fast-commit exclusion, and double `i_data_sem` write locking. On failures after partial changes, it attempts to swap inode data back and remark both inodes dirty.

## Flag and File Attribute Handling

- `ext4_ioctl_check_immutable()` prevents changing anything except the immutable bit itself while an inode is already immutable.
- `ext4_dax_dontcache()` marks non-directory dentries uncached when the persistent DAX flag changes outside forced DAX mount modes.
- `dax_compatible()` rejects DAX flag changes that conflict with mutually exclusive inode flags or verity setup.
- `ext4_ioctl_setflags()` applies user-modifiable ext4 inode flags under a journal transaction, handles DAX cache effects, ctime/version updates, journal-data flag transitions, and extents/indirect format migration.
- `ext4_ioctl_setproject()` changes project IDs when project quota support and inode extra size allow it, transferring quota usage under `xattr_sem`.

`ext4_fileattr_set()` is the VFS-facing wrapper. It masks user-visible-but-not-settable bits for compatibility with `chattr`, validates mode-specific flags, enforces immutable rules, then delegates to flag and project-ID setters.

## Filesystem Map, Extent Cache, and State Queries

- `ext4_ioc_getfsmap()` validates `FS_IOC_GETFSMAP` keys, translates external `fsmap` records to ext4 internal records, streams mappings via `ext4_getfsmap()`, and marks the final returned record with `FMR_OF_LAST`.
- `ext4_getfsmap_format()` copies one translated mapping record to userspace and tracks last-record flags.
- `ext4_ioctl_get_es_cache()` exposes the inode extent-status cache through a fiemap-shaped userspace interface while guarding against extent-count overflow.
- `EXT4_IOC_CLEAR_ES_CACHE` clears an inode's extent status cache after owner/capability checks.
- `EXT4_IOC_GETSTATE` reports selected internal inode state bits such as extent precache, new inode, new directory entry, and delayed-allocation-close state.

## Resize and Allocation Control

Handled ioctl cases include:

- `EXT4_IOC_GROUP_EXTEND`: extend the last block group.
- `EXT4_IOC_GROUP_ADD`: add a new group through `ext4_ioctl_group_add()`.
- `EXT4_IOC_RESIZE_FS`: resize to a 64-bit block count.
- `EXT4_IOC_MIGRATE`: migrate a file to extents.
- `EXT4_IOC_ALLOC_DA_BLKS`: force delayed allocation blocks.
- `EXT4_IOC_MOVE_EXT`: move extents between an original file and donor file.
- `EXT4_IOC_PRECACHE_EXTENTS`: preload extent metadata.
- `FITRIM`: discard free ranges via `ext4_trim_fs()`.

Resize operations reject bigalloc online resize, use `ext4_resize_begin()` / `ext4_resize_end()`, take write access with `mnt_want_write_file()`, mark fast commit ineligible, flush the journal when present, and register lazy inode-table initialization after successful group growth when applicable.

## Shutdown and Journal Checkpointing

- `ext4_ioctl_shutdown()` requires `CAP_SYS_ADMIN`, copies shutdown flags from userspace, and delegates to `ext4_force_shutdown()`.
- `ext4_force_shutdown()` supports default freeze/thaw shutdown, shutdown with journal commit/abort, and shutdown with journal abort but no log flush. It sets `EXT4_FLAGS_SHUTDOWN`, clears discard, traces the event, and reports shutdown through `fserror_report_shutdown()`.
- `ext4_ioctl_checkpoint()` requires `CAP_SYS_ADMIN`, validates checkpoint flags, rejects discard when the journal device cannot discard, supports dry-run mode, and calls `jbd2_journal_flush()` under the journal update lock. Zeroout checkpointing emits a ratelimited warning because it can be slow.

## Label, UUID, and Tune-Superblock Ioctls

- `ext4_ioctl_setlabel()` copies a null-terminated label with `EXT4_LABEL_MAX` enforcement, clears trailing bytes, and updates primary and backup superblocks.
- `ext4_ioctl_getlabel()` returns the current label as a padded null-terminated userspace string.
- `ext4_ioctl_getuuid()` implements length-probing and UUID retrieval through `struct fsuuid`.
- `ext4_ioctl_setuuid()` requires `CAP_SYS_ADMIN`, rejects filesystems where UUID changes would break checksum or stable-inode guarantees, validates `struct fsuuid`, then updates superblocks.
- `ext4_ioctl_get_tune_sb()` reports supported online tune operations, current tunable values, current feature flags, and masks describing which feature bits can be set or cleared online.
- `ext4_ioctl_set_tune_sb()` validates requested tune changes, translates whole-feature-set requests into set/clear masks, restricts online feature edits to supported additions, handles casefold encoding defaults, initializes directory-index hash seed defaults, and persists the changes through superblock update callbacks.

Supported online tune categories include error behavior, mount counts, check intervals, last check time, reserved blocks, reserved UID/GID, default mount options, default hash algorithm, RAID stride/stripe width, mount option string, selected feature additions, force-fsck state, and casefold encoding fields.

## Ioctl Dispatch Coverage

`__ext4_ioctl()` dispatches ext4-private and generic filesystem ioctls, including:

- Version/generation get/set.
- Online resize/group operations.
- Extent move, migration, delayed allocation, and boot-loader swap.
- Trim and extent precache.
- Fscrypt policy/key/status/nonce ioctls, gated by the encrypt feature.
- Fsverity enable/measure/metadata ioctls, gated by the verity feature.
- Extent status cache operations.
- Shutdown and checkpoint.
- Filesystem label, UUID, and tune-superblock operations.
- `FS_IOC_GETFSMAP`.

Most mutating cases explicitly acquire mount write access and perform owner/capability checks before journaling or invoking lower ext4 subsystems.

## Compat Handling

`ext4_compat_ioctl()` remaps legacy 32-bit command numbers for generation, resize reservation, and group operations. `EXT4_IOC32_GROUP_ADD` manually copies the compat structure field by field into `struct ext4_new_group_data`; other compatible pointer-based ioctls are forwarded through `compat_ptr()`. Unknown compat commands return `-ENOIOCTLCMD`.

## Dependencies

This file depends on VFS inode/file/dentry infrastructure, mount write accounting, buffer heads, block-device freeze/thaw/discard capabilities, JBD2 journaling, quota transfer, fscrypt, fsverity, fsmap translation, ext4 resize, extents, mballoc-adjacent allocation control, fast commit ineligibility tracking, DAX state, usercopy helpers, capability checks, and ext4 tracing/error reporting.

## Research Notes

`ioctl.c` is a high-risk administrative boundary because it accepts userspace-controlled operations that can mutate persistent metadata. Its dominant invariants are permission gating, feature gating, mount write acquisition, resize serialization, journal transaction ordering, checksum preservation, and careful rollback for boot-loader inode swapping. The shared superblock update callback pattern is especially important: label, UUID, tune parameters, and overhead updates all rely on it to keep primary and backup superblocks coherent.
