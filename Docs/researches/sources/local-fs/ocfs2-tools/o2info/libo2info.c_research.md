# File Research: sources/local-fs/ocfs2-tools/o2info/libo2info.c

`libo2info.c` provides offline/libocfs2 implementations for `o2info` data collection. It reads superblock fields for feature flags and volume info, reads the journal inode for mkfs-style journal size, scans slot inode allocators for free inode counts, and scans the global bitmap chain to calculate free-space fragmentation histograms.

The free-fragmentation path walks global bitmap chain records and group descriptors, counting contiguous free cluster runs, full free chunks, min/max/average extents, and histogram buckets. Values are later converted from clusters to KB by the caller/reporting code.

The FIEMAP path works on open file descriptors using `FS_IOC_FIEMAP`; it first asks for extent count, then batches extents through a stack buffer, accumulating clusters, shared/unwritten extents, holes, xattr clusters, extent counts, fragmentation percent, and score.

Dependencies include OCFS2 disk structures, bit operations, `linux/fiemap.h`, `linux/fs.h`, and verbose error helpers. Risk areas include manual bitmap scanning assumptions, static `fiemap` in `figure_extents`, and FIEMAP cluster-length truncation if extents are not cluster-aligned.
