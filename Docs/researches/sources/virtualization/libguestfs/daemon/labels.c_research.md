# File Research: sources/virtualization/libguestfs/daemon/labels.c

Dispatches filesystem label setting by filesystem type.

Important behavior:
- `do_set_label` obtains filesystem type via `do_vfs_type`.
- ext filesystems use `do_set_e2label`.
- btrfs, FAT variants, NTFS, XFS, and swap map to their helper functions.
- XFS rejects special label `"---"` because that clears labels in `xfs_admin`.
- Unsupported filesystems return `NOT_SUPPORTED`.

Filesystem relevance: central label-setting dispatcher across local filesystem families.
