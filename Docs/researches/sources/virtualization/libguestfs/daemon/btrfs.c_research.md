# File Research: sources/virtualization/libguestfs/daemon/btrfs.c

Large Btrfs daemon adapter. It wraps `btrfs`, `mkfs.btrfs`, `btrfsck`, `btrfstune`, and `btrfs-image`, validates optional arguments, and parses selected text outputs into libguestfs structs or key/value lists.

Key points:
- Optional group is available in test mode, or when the `btrfs` program exists and kernel btrfs filesystem support is available.
- Implements label get/set, filesystem resize, mkfs, subvolume snapshot/create/delete/show/set-default, sync, balance start/status/pause/cancel/resume, device add/delete, fsck, quota/qgroup operations, scrub start/cancel/resume/full/status, defragment, rescue chunk/super recover, btrfstune options, image, replace, filesystem show, and minimum-size query.
- Uses `sysroot_path` for guest filesystem paths and raw device paths for device operations.
- Mountable-based quota helpers temporarily mount Btrfs devices/subvolumes under `/tmp/btrfs.XXXXXX`, run commands, then unmount and remove the temporary mountpoint.
- Contains compatibility probes for `btrfs device add --force`, `btrfstune -u/-U`, `btrfs qgroup show --raw`, and `btrfs inspect-internal min-dev-size`.
- Parses Btrfs text output carefully for subvolume show, qgroup show, balance status, scrub status, and filesystem show, with explicit truncated/unrecognized-output errors.
- Uses PCRE2 for balance status state parsing.
- `btrfs_minimum_size` requires btrfs-progs support for `inspect-internal min-dev-size`; otherwise returns `ENOTSUP`.
