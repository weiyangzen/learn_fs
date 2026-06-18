# File Research: sources/os/bsd/openbsd-src/sbin/swapctl/swapctl.c

Command-line frontend for OpenBSD swap device management.

Supported `swapctl` commands:
- `-A`: enable all `/etc/fstab` entries of type `sw`.
- `-a path`: add a swap device/file.
- `-c -p priority path`: change swap priority.
- `-d path`: remove swap.
- `-l`: long list.
- `-s`: summary.
- `-k`: list sizes in 1K blocks.
- `-p priority`: set/filter priority.
- `-t blk|noblk`: with `-A`, restrict fstab processing by block vs non-block swap.

Compatibility mode:
- If invoked as `swapon`, accepts `-a`, `-t`, or one/more paths and calls the same add/fstab logic.

Implementation:
- Enforces mutually exclusive commands through `SET_COMMAND`.
- Uses `strtonum()` for priority validation.
- `change_priority()`, `add_swap()`, and `del_swap()` call `swapctl(SWAP_CTL/SWAP_ON/SWAP_OFF)`.
- `do_fstab()` iterates `getfsent()` entries of type `sw`, parses `priority=` and `nfsmntpt=`, optionally mounts NFS swap backing via `/sbin/mount_nfs`, rejects unsuitable object types, and enables swap.
- DUID specs are treated as block-device-like for filtering.

Filesystem/storage relevance:
- Direct block/storage administration tool for swap. It bridges `/etc/fstab`, device/file validation, NFS mount preparation, and kernel swap configuration via `swapctl(2)`.
