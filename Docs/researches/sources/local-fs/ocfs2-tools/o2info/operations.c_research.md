# File Research: sources/local-fs/ocfs2-tools/o2info/operations.c

`operations.c` implements all user-visible `o2info` operations. Each operation can use mounted-filesystem `OCFS2_IOC_INFO` ioctls or offline `libo2info` routines depending on `o2info_method`.

Operations include feature printing, volume info, mkfs option reconstruction, free inode counts, free-space fragmentation reports, file space usage, and extended filestat output. Mounted queries build `ocfs2_info_*` request structures, optionally add `OCFS2_INFO_FL_NON_COHERENT`, call the ioctl, and inspect filled/error flags.

The reporting code formats feature strings with line wrapping, renders free-fragment histograms, prints stat-like file metadata, and uses FIEMAP-derived counts for shared/unwritten/hole/xattr clusters. File-only operations reject device/libocfs2 mode.

Risk areas include several unchecked `malloc()`/`strdup()` results, freefrag argument handling assuming an argument is present, possible divide-by-zero in report percentages for unusual empty filesystems, and ioctl fallbacks that report per-request state but usually fail the whole operation.
