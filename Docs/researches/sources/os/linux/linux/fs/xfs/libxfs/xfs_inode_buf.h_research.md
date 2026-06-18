# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_buf.h

This header declares inode-buffer conversion and verification interfaces.

Key contents:
- Forward declarations for `struct xfs_inode` and `struct xfs_dinode`.
- `struct xfs_imap`, describing the disk buffer location of an inode:
  - `im_blkno`: starting basic block of the inode chunk.
  - `im_len`: chunk length in basic blocks.
  - `im_boffset`: byte offset of the inode inside the buffer.
- Prototypes for inode buffer mapping, CRC calculation, disk/in-core conversion, and dinode validation.
- Timestamp helpers:
  - `xfs_inode_encode_bigtime`
  - `xfs_inode_from_disk_ts`
- `xfs_dinode_good_version`, which enforces v3-only inode versions on v3 inode filesystems and v1/v2 otherwise.

Integration:
- Used by inode read/write paths, inode fork formatting, recovery, and verifiers.
- Provides shared declarations for code that must reason about dinode validity without owning the conversion implementation.

Risk notes:
- `xfs_dinode_good_version` encodes a core compatibility rule; misuse would allow unsupported dinode versions into higher layers.
- `xfs_imap` fields are low-level disk addressing data and must match allocation/inode geometry calculations.
