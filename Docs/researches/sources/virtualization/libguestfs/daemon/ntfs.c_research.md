# File Research: sources/virtualization/libguestfs/daemon/ntfs.c

NTFS-related command wrappers and minimum-size parser.

Important behavior:
- Availability checks for `ntfs-3g.probe` and `ntfsresize`.
- Label get/set use `ntfslabel`.
- `do_ntfs_3g_probe` runs read/write probe and returns its status.
- `do_ntfsresize` validates optional size and force flag, then runs `ntfsresize -P`.
- `ntfs_minimum_size` parses `ntfsresize --info -ff` output, including special handling for full volumes.
- `do_ntfsfix` optionally clears bad sectors with `-b`.
- `do_ntfscat_i` streams an inode via `ntfscat -i`.
- `do_ntfs_chmod` wraps `ntfssecaudit`, optionally recursive.

Filesystem relevance: NTFS metadata, repair, resizing, raw inode extraction, and ACL-mode manipulation.
