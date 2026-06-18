# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_buf.c

This file handles inode-buffer verification, conversion between on-disk dinodes and in-core inodes, dinode CRC calculation, and validation of inode metadata constraints.

Major responsibilities:
- Verify inode buffers for normal reads, readahead, and writes through `xfs_inode_buf_ops` and `xfs_inode_buf_ra_ops`.
- Map an inode location to a buffer with `xfs_imap_to_bp`.
- Convert timestamps between legacy/bigtime on-disk encodings and `timespec64`.
- Load in-core inode state from disk with `xfs_inode_from_disk`.
- Write in-core inode state to disk format with `xfs_inode_to_disk`.
- Validate dinode structure and feature constraints with `xfs_dinode_verify`.
- Validate metadata-directory inode rules with `xfs_dinode_verify_metadir`.
- Validate extent-size and COW extent-size hints.
- Compute v3 inode CRCs with `xfs_dinode_calc_crc`.

Important validation areas:
- Magic, version, inode number, UUID, CRC, and superblock feature compatibility.
- Mode/file-type validity and zero-length directory/symlink constraints.
- Fork offset and fork format consistency.
- Local, extent, btree, and metadata-btree fork limits.
- Large extent count feature and padding rules.
- Reflink/realtime compatibility.
- Bigtime feature gating.
- Metadata inode requirements: v3 only, zero permissions, root uid/gid, no DMAPI fields, required immutable/sync/noatime/nodump/nodefrag flags, and no DAX.

Integration:
- Calls fork loaders from `xfs_inode_fork.c`.
- Initializes COW fork for reflink inodes.
- Adjusts active vs metadata inode statistics for metadir inodes.
- Marks AG inode health sick when buffer reads reveal metadata corruption.

Risk notes:
- This file is a central corruption boundary; verifier changes can affect mount compatibility.
- Some historical compatibility gaps are deliberately retained for old realtime extent-size hint behavior.
- Metadata-btree validation is feature-sensitive and depends on metadir, rmapbt, reflink, and realtime feature predicates.
