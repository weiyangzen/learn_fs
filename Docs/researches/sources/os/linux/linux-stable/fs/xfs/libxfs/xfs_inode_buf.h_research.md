# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_buf.h

## Role
`xfs_inode_buf.h` declares inode-buffer mapping, dinode conversion, dinode verification, timestamp conversion, and inode hint validation interfaces.

## Main Definitions
- `struct xfs_imap` records the disk block, length, and byte offset needed to find an inode inside an inode chunk buffer.
- `xfs_inode_encode_bigtime` converts in-core timestamps into the XFS bigtime nanosecond encoding.
- `xfs_dinode_good_version` defines acceptable dinode versions based on whether the mount supports v3 inodes.

## Exported API
- Buffer/dinode access: `xfs_imap_to_bp`.
- Disk/in-core conversion: `xfs_inode_from_disk`, `xfs_inode_to_disk`, and `xfs_inode_from_disk_ts`.
- Integrity: `xfs_dinode_calc_crc`, `xfs_dinode_verify`, and `xfs_dinode_verify_metadir`.
- Hint validation: `xfs_inode_validate_extsize` and `xfs_inode_validate_cowextsize`.

## Dependencies
The header depends on XFS mount, inode, dinode, transaction, timestamp, and fail-address types supplied by surrounding libxfs headers.

## Research Notes
This header is the compact contract for inode core verification and conversion. It separates inode-buffer location (`xfs_imap`) from dinode semantic validation.
