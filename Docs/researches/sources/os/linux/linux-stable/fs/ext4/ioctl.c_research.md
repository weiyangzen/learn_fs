# File Research: sources/os/linux/linux-stable/fs/ext4/ioctl.c

## Summary
Implements ext4's ioctl and file-attribute control plane. This file handles user-visible administrative operations for inode versions, extent migration, online resize, extent movement, delayed allocation flushing, boot-loader inode swapping, trim/discard, encryption and verity ioctls, extent-status cache inspection, forced shutdown, journal checkpointing, filesystem label/UUID mutation, tune-superblock parameters, and persistent overhead updates.

## Main Responsibilities
- Dispatches ext4-specific and generic filesystem ioctls through `__ext4_ioctl()`.
- Provides 32-bit compatibility translation in `ext4_compat_ioctl()`.
- Updates primary and backup superblocks through a callback-based helper used for label, UUID, tune parameters, and overhead-cluster changes.
- Implements file attribute get/set integration for VFS `fileattr` APIs, including ext4 user-visible flags and project IDs.
- Enforces capability, ownership, write-mount, feature, immutable, DAX, quota-file, journaling, and readonly constraints before mutating filesystem state.
- Wraps online resize operations and ensures journal flushing / fast-commit ineligibility after resize.
- Routes fscrypt and fsverity ioctl requests only when corresponding ext4 features are enabled.

## Superblock Update Path
`ext4_update_primary_sb()` journals and updates the mounted primary superblock buffer, calls a caller-supplied `ext4_update_sb_callback`, recomputes the primary checksum, handles previous write I/O errors, dirties metadata, and synchronously writes the buffer.

`ext4_update_backup_sb()` updates one backup superblock if the target group has one. It handles group-0 offset rules, validates metadata checksums before modification, optionally journals the buffer, recomputes backup checksums when enabled, marks or journals the buffer dirty, and synchronously writes it.

`ext4_update_superblocks_fn()` serializes against online resize with `EXT4_FLAGS_RESIZING`, starts a journal transaction for the primary superblock plus at most two backups, then walks sparse-super backup groups via `ext4_list_backups()`. After two successful backup updates, remaining backups are written without a journal. The file explicitly relies on fsck being able to repair backup-superblock divergence if a late non-journaled backup update is interrupted.

Callback users include:
- `ext4_sb_setlabel()` for volume labels.
- `ext4_sb_setuuid()` for filesystem UUID.
- `ext4_sb_setparams()` for tune-superblock parameters.
- `set_overhead()` for `s_overhead_clusters`.

## Inode and File Attribute Mutation
`ext4_fileattr_get()` reports ext4 visible flags and project ID through `struct file_kattr`, masking `FS_PROJINHERIT_FL` for regular files.

`ext4_fileattr_set()` validates requested flags against `EXT4_FL_USER_VISIBLE`, masks to `EXT4_FL_USER_MODIFIABLE`, applies mode-specific flag masking, checks immutable-file restrictions, then calls `ext4_ioctl_setflags()` and `ext4_ioctl_setproject()`.

`ext4_ioctl_setflags()` protects quota files, requires `CAP_SYS_RESOURCE` for journal-data mode changes, validates DAX mutual exclusions, validates casefold enablement only for empty directories on casefold-capable filesystems, flushes regular-file pages before setting immutable, journals inode flag updates, updates ctime and inode version, drops DAX inode cache state when needed, and performs post-transaction journal-mode or extents/indirect-format migration.

`ext4_ioctl_setproject()` exists in a quota-enabled and quota-disabled form. With quotas enabled, it requires project feature support and large-enough inodes, expands extra inode size if needed, initializes quotas, transfers project quota accounting under `xattr_sem`, updates `i_projid`, and journals the inode. Without quota support, only the default project ID is accepted.

`ext4_ioctl_check_immutable()` prevents changing any inode state other than setting immutable itself while immutable is already set, including project ID changes.

## Boot Loader Inode Swap
`swap_inode_boot_loader()` swaps a regular file with `EXT4_BOOT_LOADER_INO`. It:
- Loads the special inode with `EXT4_IGET_SPECIAL | EXT4_IGET_BAD`.
- Locks both inodes and rejects multi-link, non-regular, swapfile, encrypted, journal-data, and inline-data files.
- Requires owner/capability permission plus `CAP_SYS_ADMIN`.
- Flushes and invalidates page cache, waits for direct I/O, and truncates cached pages.
- Starts a move-extents journal transaction and marks fast commit ineligible.
- Initializes the boot-loader inode if it has never been a regular file.
- Swaps extent/inline `i_data`, selected ext4 flags, timestamps, inode version, sizes, and disk sizes through `swap_inode_data()`.
- Regenerates inode generations and metadata checksum seeds via `ext4_reset_inode_seed()`.
- Marks both inodes dirty and adjusts quota accounting so the boot-loader inode is not charged.
- Reverts the swap on inode dirtying or quota-transfer failure.

This path is heavily ordered around page-cache invalidation, direct-I/O drain, `i_data_sem`, journaling, and quota updates.

## Online Resize and Allocation-Related Ioctls
`EXT4_IOC_GROUP_EXTEND`, `EXT4_IOC_GROUP_ADD`, and `EXT4_IOC_RESIZE_FS` all enter `ext4_resize_begin()` / `ext4_resize_end()`, reject bigalloc where unsupported, require write access, call the appropriate resize helper, mark fast commit ineligible, flush the journal when present, and register lazy inode-table initialization when a new group is added on group-descriptor-checksummed filesystems.

`EXT4_IOC_MOVE_EXT` validates read/write access on the original file, writable donor fd, copies `struct move_extent`, calls `ext4_move_extents()`, and copies back `moved_len`.

`EXT4_IOC_MIGRATE` requires inode ownership/capability, write access, inode lock, and calls `ext4_ext_migrate()`.

`EXT4_IOC_ALLOC_DA_BLKS` forces delayed allocation blocks through `ext4_alloc_da_blocks()`.

`EXT4_IOC_PRECACHE_EXTENTS` takes a shared inode lock and calls `ext4_ext_precache()`.

## Mapping, Cache, Trim, Shutdown, and Checkpoint
`FS_IOC_GETFSMAP` is handled by `ext4_ioc_getfsmap()`, which validates reserved fields and allowed file-offset sentinel values, converts external keys to internal ext4 fsmap keys, invokes `ext4_getfsmap()`, copies records through `ext4_getfsmap_format()`, and marks the last record with `FMR_OF_LAST` when appropriate.

`EXT4_IOC_GET_ES_CACHE` copies a `struct fiemap`, validates extent count against `FIEMAP_MAX_EXTENTS`, calls `ext4_get_es_cache()`, and copies mapped extent counts and flags back to userspace. `EXT4_IOC_CLEAR_ES_CACHE` requires ownership/capability and clears the inode extent-status cache.

`FITRIM` requires `CAP_SYS_ADMIN`, discard support, and a journal-replayed filesystem. It rejects `NOLOAD` journaled mounts, calls `ext4_trim_fs()`, and returns the updated trim range.

`EXT4_IOC_SHUTDOWN` requires `CAP_SYS_ADMIN` and calls `ext4_force_shutdown()`. Shutdown supports default freeze/thaw, journal flush+abort, and no-flush abort modes, sets `EXT4_FLAGS_SHUTDOWN`, disables discard, traces the event, and reports filesystem shutdown to `fserror`.

`EXT4_IOC_CHECKPOINT` requires `CAP_SYS_ADMIN`, validates dry-run/discard/zeroout flags, requires a journal, checks discard support for journal-device discard, optionally returns early for dry run, and flushes the JBD2 journal under update lock. Zeroout emits a ratelimited warning because it can be slow.

`EXT4_IOC_GETSTATE` returns selected transient inode state bits such as extent precached, new inode, new directory entry, and delayed-allocation-on-close.

## Label, UUID, and Tune-Superblock Ioctls
`FS_IOC_GETFSLABEL` reads `s_volume_name` under the superblock buffer lock and returns a NUL-padded label. `FS_IOC_SETFSLABEL` requires `CAP_SYS_ADMIN`, copies at most `EXT4_LABEL_MAX + 1`, rejects overlong labels, zero-fills unused bytes, obtains write access, and updates primary/backups through the superblock callback path.

`EXT4_IOC_GETFSUUID` implements the `struct fsuuid` length-query convention. If `fsu_len` is zero, it writes back the required UUID size. Otherwise it requires length at least `UUID_SIZE`, zero flags, copies the UUID under the superblock buffer lock, and returns both header and UUID bytes.

`EXT4_IOC_SETFSUUID` requires `CAP_SYS_ADMIN`, rejects UUID changes when checksummed descriptors/metadata lack `csum_seed`, and rejects `stable_inodes`. It validates `struct fsuuid`, copies the UUID, obtains write access, and updates all relevant superblocks.

`EXT4_IOC_GET_TUNE_SB_PARAM` returns supported tune flags, current error behavior, mount counts, check interval/time, reserved blocks and IDs, default mount options, hash algorithm, RAID stride/stripe width, encoding fields, mount option string, feature masks, and masks describing which features can be set or cleared online.

`EXT4_IOC_SET_TUNE_SB_PARAM` validates capability, mount option string termination, supported operation flags, error behavior range, reserved-block limit, hash algorithm, mutually exclusive absolute-feature and edit-feature modes, and supported set/clear feature masks. It can translate absolute feature masks into set/clear operations. Supported online feature enabling includes dir_index, stable_inodes, extents, ea_inode, encrypt, csum_seed, largedir, casefold, large_file, dir_nlink, extra_isize, project, and verity; clearing feature bits is not supported. Enabling casefold auto-fills UTF-8 encoding defaults, validates encoding flags, and enabling dir_index initializes hash seed/default hash metadata if needed.

## Ioctl Dispatch
`__ext4_ioctl()` handles:
- `FS_IOC_GETFSMAP`.
- `EXT4_IOC_GETVERSION` / old variant.
- `EXT4_IOC_SETVERSION` / old variant, rejected when `metadata_csum` is enabled.
- Online resize ioctls: group extend, group add, resize fs.
- `EXT4_IOC_MOVE_EXT`, `EXT4_IOC_MIGRATE`, `EXT4_IOC_ALLOC_DA_BLKS`, `EXT4_IOC_SWAP_BOOT`.
- `FITRIM`.
- Extent precache and extent-status cache ioctls.
- fscrypt policy/key/nonce ioctls gated by `encrypt`.
- shutdown, checkpoint, label, UUID, tune-superblock ioctls.
- fsverity enable/measure/read-metadata ioctls gated by `verity`.

Unrecognized commands return `-ENOTTY`.

`ext4_ioctl()` is the thin public wrapper. `ext4_compat_ioctl()` remaps legacy 32-bit command numbers and handles compat group-add structure unpacking before delegating to `ext4_ioctl()` with a compat pointer.

## Synchronization and Lifetime
- Superblock mutations use buffer locks and journal write access where available.
- `EXT4_FLAGS_RESIZING` serializes superblock-wide updates against online resize.
- Write-intent operations use `mnt_want_write_file()` / `mnt_drop_write_file()`.
- Inode mutations use inode locks, quota initialization, `xattr_sem`, `i_data_sem`, direct-I/O waits, and page-cache writeback/invalidation depending on operation.
- Journal-sensitive operations mark fast commit ineligible for resize and boot-loader swap.
- Forced shutdown interacts with block-device freeze/thaw and JBD2 abort/flush semantics.

## Dependencies
Depends on ext4 core headers, JBD2 wrappers, resize, extents, mballoc-adjacent allocation state, fsmap conversion helpers, VFS ioctl/fileattr APIs, fscrypt, fsverity, quota APIs, buffer-head operations, block-device discard/freeze APIs, tracepoints, usercopy helpers, and filesystem error reporting.

## Risks
This file exposes high-privilege mutation paths directly to userspace, so validation is central. Risk areas include superblock backup update ordering, non-journaled backup writes, online feature enabling, UUID changes under checksum/stable-inode constraints, DAX flag interactions, immutable-file semantics, quota transfer during project-ID and boot-loader swap operations, resize journal flushing, and forced shutdown races with in-flight filesystem activity.
