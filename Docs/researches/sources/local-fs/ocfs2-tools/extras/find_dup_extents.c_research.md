# File Research: sources/local-fs/ocfs2-tools/extras/find_dup_extents.c

Read coverage: complete file read, 287 lines.

Purpose: scans all valid inodes and reports data clusters claimed by more than one extent tree.

Behavior:
- Opens the volume read-only.
- Creates a cluster bitmap for seen extents and another for duplicate clusters.
- First inode scan marks every data extent cluster and records duplicate cluster bits.
- If duplicates were found, a second inode scan reports each inode and cluster that intersects the duplicate bitmap.
- Skips invalid inodes, selected system metadata inodes, and fast symlinks without allocated clusters.

Dependencies: OCFS2 inode scanner, extent iterator, cluster bitmap APIs, `ocfs2_rec_clusters()`, and block-to-cluster conversion.

Risk notes:
- Read-only diagnostic.
- Main exits `0` even on some scan/open errors after printing `com_err()`, so shell callers cannot rely on status alone.
- It reports duplicate physical clusters but does not resolve whether they are legitimate refcounted/reflink sharing.
