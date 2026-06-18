# File Research: sources/local-fs/gfs2-utils/tests/atlocal.in

Autotest local configuration fragment.

Defines:
- `GFS_TGT="@testvol@"`
- `GFS_TGT_SZ=20`
- `GFS_MKFS="mkfs.gfs2 -O -D"`

Provides:
- `gfs_max_blocks(blocksize)`: computes maximum blocks for the test volume size.
- `gfs_tgt_cleanup(flag)`: removes the test volume when requested.
- EXIT trap invoking cleanup.

Research notes:
- Test mkfs defaults force override and debug modes.
