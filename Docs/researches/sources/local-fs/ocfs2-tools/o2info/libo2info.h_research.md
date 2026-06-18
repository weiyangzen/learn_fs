# File Research: sources/local-fs/ocfs2-tools/o2info/libo2info.h

This header defines the shared data model for `o2info` collection routines: filesystem feature bitsets, volume info, mkfs reconstruction data, per-slot free inode counts, free-fragmentation statistics/histogram, and FIEMAP-derived file layout statistics.

It exposes library entry points for offline OCFS2 filesystem queries and descriptor-based FIEMAP queries. Constants include `DEFAULT_CHUNKSIZE` and histogram sizing delegates to `OCFS2_INFO_MAX_HIST`.

The header is the contract between `libo2info.c` and `operations.c`; callers fill these structures either through libocfs2 or through mounted-filesystem ioctls before formatting output.
