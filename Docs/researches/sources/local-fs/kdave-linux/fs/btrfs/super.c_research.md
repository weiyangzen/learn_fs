# File Research: sources/local-fs/kdave-linux/fs/btrfs/super.c

Read coverage: complete file, 2711 lines.

This file implements the Btrfs Linux filesystem registration, mount/fs_context parsing, superblock operations, remount handling, statfs reporting, `/dev/btrfs-control`, freeze/unfreeze checks, and module init/exit sequencing.

Main responsibilities:
- Defines `btrfs_fs_context` and parses mount parameters through the new mount API.
- Validates option combinations, rescue options, zoned constraints, free-space-cache constraints, compression settings, and readonly-only recovery options.
- Opens/scans devices, creates or reuses superblocks, fills the superblock, and mounts the selected subvolume.
- Supports subvolume mounts with differing mount read-only/read-write state via internal reconfigure compatibility logic.
- Implements `sync_fs`, `show_options`, `statfs`, freeze/unfreeze, device removal notification, shrinker callbacks, and shutdown.
- Registers the `btrfs` filesystem type and `/dev/btrfs-control` misc device.
- Runs ordered subsystem initialization and reverse cleanup for the module.

Important flows:
- `btrfs_parse_param()` handles all user mount options and stores them in `btrfs_fs_context`.
- `btrfs_check_options()` enforces readonly-only rescue flags, free-space-tree constraints, zoned options, and deprecation warnings.
- `btrfs_set_free_space_cache_settings()` derives v1/v2 free-space cache behavior from mount options and on-disk features; it forces free-space-tree for subpage sector/page mismatch.
- `btrfs_get_tree_subvol()` allocates temporary `fs_info`, duplicates fs_context, mounts the whole filesystem, reconfigures if needed, then mounts the selected subvolume subtree.
- `btrfs_fill_super()` sets VFS superblock callbacks, opens the ctree, emits options, and installs the root inode/dentry.
- `btrfs_reconfigure()` applies remount options, handles RO/RW transitions, resizes worker pools, reconciles free-space-tree option state, and restores old context on failure.
- `btrfs_statfs()` combines allocated data/metadata free space, readonly block-group adjustments, simulated data allocation availability, global reserve accounting, and subvolume-specific fsid.
- `btrfs_freeze()` commits current transactions; `btrfs_unfreeze()` rereads device superblocks to detect unexpected external modification before clearing frozen state.
- `init_btrfs_fs()` walks `mod_init_seq`; failed initialization unwinds initialized components in reverse.

Concurrency and lifetime:
- Device scanning/opening is coordinated under `uuid_mutex`, but `sget_fc()` is called without holding it to avoid lock-order inversion.
- Existing superblock reuse leaves the temporary fs_context-owned `fs_info` for later cleanup.
- Remount-to-readonly cancels reclaim work, cleans discard state, waits for cleaner/uuid/qgroup/scrub/balance activity, and commits the superblock.
- Freeze/unfreeze assumes the filesystem remains frozen while validating device superblocks.

Integration points:
- Includes and coordinates most Btrfs subsystems: disk-io, transactions, compression, dev replace, free-space cache/tree, qgroups, scrub, raid56, zoned mode, verity, ioctl, sysfs, and space-info.
- Exports functions declared in `super.h`: option checking, sync, subvolume-name lookup, and free-space-cache settings.

Risk notes:
- Mount option interactions are compatibility-sensitive ABI: compression vs nodatacow/nodatasum, rescue aliases, deprecated options, and old/new mount API readonly semantics.
- Subvolume mount handling relies on careful fs_context duplication and ownership transfer.
- `statfs` availability is approximate by design and must remain pessimistic when metadata is exhausted.
- Unfreeze validation deliberately returns success after marking the filesystem errored so VFS can unfreeze safely.
