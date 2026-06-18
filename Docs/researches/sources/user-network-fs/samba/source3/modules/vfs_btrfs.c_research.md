# sources/user-network-fs/samba/source3/modules/vfs_btrfs.c

## Purpose
`vfs_btrfs.c` exposes Btrfs-specific behavior to Samba shares. It advertises compression/block-refcounting support, maps SMB compression requests to Linux inode flags, and optionally implements Samba snapshot create/delete hooks using Btrfs subvolume ioctls with `@GMT-` names compatible with shadow-copy consumers.

## Important APIs, types, and functions
- `btrfs_fs_capabilities()` extends downstream filesystem capabilities with `FILE_FILE_COMPRESSION` and `FILE_SUPPORTS_BLOCK_REFCOUNTING`.
- `btrfs_fget_compression()` reads `FS_IOC_GETFLAGS` and reports `COMPRESSION_FORMAT_LZNT1` when `FS_COMPR_FL` is set, using `/proc/self/fd` for pathref handles when available.
- `btrfs_set_compression()` reads and writes `FS_COMPR_FL` with `FS_IOC_GETFLAGS` and `FS_IOC_SETFLAGS`.
- `btrfs_snap_check_path()` accepts only Btrfs subvolume roots when `btrfs:manipulate snapshots = yes`; otherwise it delegates to the next VFS module.
- `btrfs_gen_snap_dest_path()` generates `@GMT-%Y.%m.%d-%H.%M.%S` names in UTC.
- `btrfs_snap_create()` uses `BTRFS_IOC_SNAP_CREATE_V2`, optionally setting `BTRFS_SUBVOL_RDONLY` for read-only snapshots.
- `btrfs_snap_delete()` validates the snapshot basename with `strptime()` and destroys it with `BTRFS_IOC_SNAP_DESTROY`.
- `vfs_btrfs_init()` registers the module as `btrfs`.

## Control flow
Capability and compression calls are direct wrappers around Linux ioctl state. Compression get handles normal file descriptors first, then pathref descriptors via `/proc` if Samba recorded proc-fd support. Compression set requires a usable IO fd and accepts `NONE`, `DEFAULT`, or `LZNT1`, using Samba's compression constants as SMB-facing signals rather than Btrfs algorithm selectors.

Snapshot hooks are gated by `btrfs:manipulate snapshots`. When disabled, all snapshot operations pass through to the next VFS module. When enabled, `snap_check_path` verifies the share path is a directory with inode `256`, matching Btrfs subvolume root convention. Create opens the source subvolume and destination directory, fills the Btrfs ioctl argument with the source fd and generated subvolume name, temporarily escalates with `become_root()`, and returns both base and snapshot paths. Delete splits `snap_path` with `dirname()`/`basename()`, confirms the basename matches the exact Samba shadow-copy timestamp format, then performs the destroy ioctl as root.

## State and persistence behavior
The module persists changes in filesystem metadata: compression inode flags and Btrfs subvolumes. It stores no long-lived in-memory state. Snapshot timestamps are encoded in directory names, making the snapshot namespace itself the persistence layer.

## Dependencies and integration points
This file depends on Linux `FS_IOC_*` flags, Btrfs ioctl ABI structs/constants, Samba VFS snapshot hooks, `become_root()` privilege handling, talloc, and timestamp utilities. It is registered as `vfs_btrfs` in `wscript_build`; consumers usually combine it with snapshot-aware clients or Samba shadow-copy logic.

## Risks and edge cases
- The compression mapping reports Btrfs compression as `LZNT1`, which is a Windows-facing compatibility value and not a Btrfs algorithm choice.
- `btrfs_set_compression()` debug messages appear inverted: clearing compression says "setting compression" and setting `FS_COMPR_FL` says "clearing compression".
- Snapshot manipulation requires root and can destroy subvolumes; the strict name-format check reduces but does not remove operational risk.
- Subvolume detection by inode `256` follows Btrfs convention but is still a filesystem-specific assumption.
- Large fixed ioctl name buffers are intentionally not fully zeroed; name length checks must remain correct.

## Test signals
No direct tests were found in this subset. Useful validation requires a Btrfs-backed share: check advertised SMB capabilities, query/set compression through SMB, create read-only and read-write snapshots with `btrfs:manipulate snapshots = yes`, reject non-subvolume paths, and ensure malformed snapshot names are not deleted. Build registration in `wscript_build` is the static integration signal.
