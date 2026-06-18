# File Research: sources/local-fs/f2fs-tools/fsck/quotaio_v2.h

Purpose: declares on-disk structures and constants for the VFS v1 quota file format used by `quotaio_v2.c`.

Key contents:
- Defines `V2_DQINFOOFF` as the offset immediately after `struct v2_disk_dqheader`.
- Defines supported `V2_VERSION` as `1`.
- Defines `struct v2_disk_dqheader` with magic and version, asserted to 8 bytes.
- Defines `V2_DQF_MASK` for valid on-disk quota flags.
- Defines `struct v2_disk_dqinfo` with block/inode grace times, flags, qtree block count, free block, and free-entry heads, asserted to 24 bytes.
- Defines `struct v2r1_disk_dqblk`, the 72-byte disk quota record with ID, inode limits/current count, block limits/current space, and grace timers.

Important dependencies:
- Includes `quotaio.h`, which in turn pulls in quota and F2FS shared types.
- Consumed by V2 quota conversion and initialization code.

Risk notes:
- The structure definitions are exact on-disk ABI and protected by static assertions; changes here would affect quota file compatibility.
