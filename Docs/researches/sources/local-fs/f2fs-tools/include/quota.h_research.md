# File Research: sources/local-fs/f2fs-tools/include/quota.h

Defines quota file constants and disk structures used by `mkfs.f2fs` when creating quota inodes.

Key contents:
- Quota types: user, group, project, and `MAXQUOTAS`.
- Bit masks for enabled quota types: `QUOTA_USR_BIT`, `QUOTA_GRP_BIT`, `QUOTA_PRJ_BIT`, `QUOTA_ALL_BIT`.
- Current quota file magic values via `INITQMAGICS`.
- Quota timing defaults: one-week inode and block grace periods.
- `QT_TREEOFF` and `V2_DQINFOOFF` offsets.
- Disk structs:
  - `v2_disk_dqheader`: magic and version.
  - `v2_disk_dqinfo`: grace periods, flags, block count, free block, free entry.
  - `v2r1_disk_dqblk`: quota id, inode limits/counts, block limits/current space, timers.
- `static_assert` guards expected serialized sizes.

Usage:
- `mkfs/f2fs_format.c` uses this header to synthesize initial quota file contents for enabled user/group/project quota features.
