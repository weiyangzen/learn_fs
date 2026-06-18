# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.h

## Role

This header declares inode buffer mapping, dinode verification, disk/incore conversion, CRC, timestamp, and extent-size validation interfaces.

## Main Contents

- `struct xfs_imap` records an inode chunk disk address, length, and byte offset.
- `xfs_imap_to_bp` reads the buffer containing a mapped inode.
- `xfs_dinode_calc_crc` updates a v3 dinode checksum.
- `xfs_inode_to_disk` and `xfs_inode_from_disk` convert between incore inode and on-disk dinode.
- `xfs_dinode_verify` and `xfs_dinode_verify_metadir` validate inode metadata.
- `xfs_inode_validate_extsize` and `xfs_inode_validate_cowextsize` validate allocation hint fields.
- `xfs_inode_encode_bigtime` encodes an incore timestamp into XFS bigtime units.
- `xfs_inode_from_disk_ts` decodes a dinode timestamp.
- `xfs_dinode_good_version` accepts v3 only for v3 inode filesystems, otherwise v1/v2.

## Dependencies

The header exposes types from mount, inode, dinode, timestamp, and buffer code. It is consumed by inode loading, inode flushing, repair, mkfs, and verifier code.

## Research Notes

This is a narrow public contract for inode core serialization and verification. The inline version rule is important because inode buffer verification uses it before deeper dinode validation.
