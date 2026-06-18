# File Research: sources/os/linux/linux/fs/quota/quotaio_v2.h

On-disk structure definitions and constants for v2 quota files.

Defines:
- `V2_INITQMAGICS` for user, group, and project quota files.
- `V2_INITQVERSIONS`, currently version 1 for each quota type.
- `struct v2_disk_dqheader`, the file magic/version header.
- `struct v2r0_disk_dqblk`, v2 revision 0 quota entry with 32-bit limit fields and 64-bit space/timer fields.
- `struct v2r1_disk_dqblk`, v2 revision 1 quota entry with 64-bit limit/counter fields.
- `struct v2_disk_dqinfo`, global info header containing grace times, flags, total blocks, free block head, and free-entry head.
- `V2_DQINFOOFF`, the offset of the info header after the file header.
- `V2_DQBLKSIZE_BITS`, setting v2 quota tree blocks to 1024 bytes.

Research notes:
- These definitions are consumed by `quota_v2.c` and interpreted by the generic tree code in `quota_tree.c`.
