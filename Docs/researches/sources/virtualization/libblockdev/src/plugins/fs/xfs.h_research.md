# File Research: sources/virtualization/libblockdev/src/plugins/fs/xfs.h

Declares XFS info data and operations.

Key contents:
- Defines `BDFSXfsInfo` with `label`, `uuid`, `block_size`, and `block_count`.
- Declares copy/free helpers.
- Declares mkfs, check, repair, label, UUID, info, and resize APIs.

Important invariants:
- XFS resize takes a mountpoint and filesystem-block count, not a device byte size.
- Returned info values are sufficient for size calculation as `block_size * block_count`.

Filesystem/block relevance:
- Exposes XFS management operations to generic dispatch and mount-assisted resize handling.

Notable risks:
- Callers using this header directly must know that `bd_fs_xfs_resize()` expects a mounted path rather than a block device.
