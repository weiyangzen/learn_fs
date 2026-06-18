# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_discard.c

Implements discard/TRIM helpers for JFS.

Key functions:
- `jfs_issue_discard()` calls `sb_issue_discard()` for a block range and logs failures/info through JFS debug macros.
- `jfs_ioc_trim()` converts user byte range/minlen to filesystem blocks, validates against bmap state, clamps end to map size, computes allocation group range, and calls `dbDiscardAG()` for each AG.

Integration:
- Called from `FITRIM` ioctl and from allocation-map free paths when online discard is enabled.
- Uses `s_umount` read lock while consulting the bmap and trimming.

Risk notes:
- Trims entire allocation groups intersecting the requested range; fine-grained range filtering is effectively at AG selection granularity.
- Returns `-EINVAL` for missing bmap, too-large minlen, out-of-range start, or sub-block range length.
