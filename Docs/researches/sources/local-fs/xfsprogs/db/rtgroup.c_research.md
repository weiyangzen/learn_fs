# File Research: sources/local-fs/xfsprogs/db/rtgroup.c

Defines `xfs_db` support for realtime group metadata types.

Key responsibilities:
- Registers the `rtsb` command when the mounted filesystem has realtime groups.
- Defines field tables for realtime superblock (`rtsb`), realtime group bitmap (`rgbitmap`), and realtime group summary (`rgsummary`) structures.
- Provides size/count helpers for displaying realtime metadata blocks.
- Seeks to the realtime superblock at `XFS_RTSB_DADDR` via `set_rt_cur`.

Important behavior:
- `rtsb_init` only exposes the command for filesystems with realtime groups.
- `rtwords_count` subtracts the `xfs_rtbuf_blkinfo` header for rtgroup-enabled filesystems before counting bitmap/summary words.
- `rtsb_size` reports the current filesystem block size in bits.

Dependencies:
- Uses `type`, `field`, `io`, `sb`, and realtime buffer type definitions.
- Depends on `xfs_has_rtgroups`, `set_rt_cur`, `mp`, and `typtab`.

Notable risks:
- The field layouts must match ondisk realtime group structures exactly.
- `rtsb_f` assumes `TYP_RTSB` is registered in the active type table.
