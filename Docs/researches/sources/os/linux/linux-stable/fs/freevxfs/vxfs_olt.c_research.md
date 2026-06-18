# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_olt.c

This file reads and parses the VxFS Object Location Table, which tells the driver where key filesystem metadata objects live.

Major responsibilities:
- Convert OLT block addresses from VxFS block size to current superblock block units.
- Read the OLT extent from disk.
- Validate the OLT magic number.
- Parse OLT entries to find the fileset header inode and initial inode-list extent.
- Store discovered values in `vxfs_sb_info`.

Important design points:
- Only the first OLT extent is supported; `vsi_oltsize > 1` is rejected with a notice.
- The parser walks variable-sized OLT records using each record's `olt_size`.
- Only the `VXFS_OLT_FSHEAD` and `VXFS_OLT_ILIST` records are acted upon; other record types are ignored.
- The helper functions assert that `vsi_fshino` and `vsi_iext` were not already set.

Key invariants:
- OLT magic must match `VXFS_OLT_MAGIC` after byte-order conversion.
- Successful parsing requires both a fileset header inode number and an initial inode-list extent.
- On failure, the buffer head is released and `-EINVAL` is returned.

External interfaces:
- Provides `vxfs_read_olt()` for `vxfs_fill_super()`.
