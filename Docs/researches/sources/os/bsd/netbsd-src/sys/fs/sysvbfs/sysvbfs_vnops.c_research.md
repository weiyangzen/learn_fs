# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_vnops.c

Read completely: 925 lines.

This implements sysvbfs vnode operations for a flat System V BFS filesystem. Lookup recognizes `.` and ordinary root-level files, denies write operations on read-only mounts, checks directory execute/write permissions, and resolves BFS dirents to vnodes. Create delegates to `bfs_file_create`, then loads the new vnode and marks timestamps dirty. Open initializes cached size and data-block state, with non-append writes starting from size zero.

Access, getattr, setattr, and timestamp update map NetBSD vnode attributes onto BFS inode attributes. Read and write use UBC over the vnode object; write resizes contiguous BFS extents through `sysvbfs_file_setsize`. Remove and rename delegate to BFS delete/rename helpers, readdir emits fixed-size `struct dirent` records from the BFS dirent array, and bmap/strategy translate logical file blocks to contiguous device sectors.

Important interactions: relies heavily on the BFS implementation for allocation, dirent lookup, inode lookup/delete, file create/delete/rename, and metadata persistence. Uses `lf_advlock` for byte-range locks and genfs for paging support.

Security/reliability notes: `sysvbfs_rename` computes errors but returns `0` unconditionally at function end, which can hide `EXDEV` or BFS failures. The filesystem model is intentionally limited: one directory, no links, no symlinks, no subdirectories, and 14-byte names.
