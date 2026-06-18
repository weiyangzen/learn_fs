# File Research: sources/local-fs/xfsprogs/db/rtgroup.h

Header for `xfs_db` realtime group display support.

Key responsibilities:
- Declares field tables for realtime superblock, realtime group bitmap, and realtime group summary objects.
- Declares `rtsb_init` and `rtsb_size`.

Dependencies:
- Consumed by `rtgroup.c` and the type registry in `type.c`.

Notable risks:
- Any enum/type-table changes for realtime metadata must keep these declarations and `type.c` synchronized.
