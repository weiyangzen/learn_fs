# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_alloc.c

This file implements UFS block, fragment, inode, preallocation, and free-space allocation policy. It bridges quota accounting, cylinder-group bitmaps, rotational layout, UFS logging metadata tracking, and filesystem lock coordination.

`alloc` allocates a block or fragment for an inode. It validates size, checks filesystem free space and minfree privilege, reserves block quota through `chkdq`, chooses a preferred cylinder group, and calls `hashalloc` with `alloccg`. If physical allocation loses a race after quota reservation, it rolls quota back. Full-filesystem warnings are rate-limited through `vfs_lastwhinetime`.

`realloccg` grows an existing fragment. It reserves quota for the size delta, first tries `fragextend` to extend in place, then falls back to allocating either a full block under `FS_OPTTIME` or exactly the requested fragment run under space optimization. Unused fragments from a full-block allocation are immediately freed. Failed allocation rolls back the quota delta.

`ufs_ialloc` allocates an inode. It charges inode quota except for shadow inodes and extended attribute directory inodes, finds a free inode through `hashalloc`/`ialloccg`, then obtains and initializes the inode. If the supposedly free inode is unexpectedly allocated, it marks it `ISTALE`, warns to run fsck, and retries. If stale size or block pointers remain on a free inode, it clears them defensively to avoid exposing old data, accepting that fsck may later report unaccounted blocks.

`dirpref` chooses a cylinder group for new directories. With `ufs_close_dirs` enabled, it prefers the current or first cylinder group with more than 25% free inodes and blocks; otherwise it falls back to the traditional policy of choosing a group with at least average free inodes and few directories.

`blkpref` chooses the preferred physical location for the next logical block. It keeps early direct blocks near the inode's cylinder group, starts later block groups in cylinder groups with above-average free blocks, and otherwise prefers contiguous blocks up to `fs_maxcontig`, adding rotational delay spacing when configured. It also understands negative fallocate block markers by converting them back into positive physical preferences.

`free` returns blocks or fragments to a cylinder group bitmap. It handles negative fallocate block numbers, validates size and block range, cancels logging reservations unless told not to, marks metadata frees, updates free block/fragment summaries, fragment summary buckets, rotational summaries, delete-queue accounting for logged filesystems, superblock summary state, and cylinder group buffers. It detects attempts to free already-free blocks or fragments and reports filesystem faults.

`ufs_ifree` returns an inode to the cylinder group inode bitmap, validates range and current mode, updates the inode rotor, free inode counts, directory counts, clean state, and logging metadata. It reports double-free and range corruption through `ufs_fault`.

The lower-level allocation helpers are `hashalloc`, `fragextend`, `alloccg`, `alloccgblk`, `ialloccg`, and `mapsearch`. `hashalloc` tries the preferred cylinder group, quadratic rehash, then brute-force search. `alloccg` allocates either full blocks or fragments, splitting a full block when needed. `alloccgblk` honors an exact preferred block, then same-cylinder rotational layout, then the cylinder-group block rotor. `mapsearch` scans the fragment bitmap for a matching run while avoiding blocks on the logging cancel list.

`ufs_allocsp` implements UFS preallocation/fallocate. It write-locks the filesystem, holds `i_rwlock` across the operation, allocates direct blocks normally, then allocates indirect-referenced blocks as negative block numbers to mark preallocated-but-unwritten storage. It breaks the work into `vfs_iotransz` transactions, yields the filesystem write lock to waiters between chunks, sets `IFALLOCATE` on success or partial interruption, updates large-file superblock state, and rolls back direct and indirect allocations on error using saved direct block state and an undo list.

`ufs_freesp` implements the supported free-space operation: `l_len == 0`, meaning truncate/free from `l_start` to EOF. It checks mandatory locks, takes `i_rwlock` to exclude block allocation, and delegates to `TRANS_ITRUNC`.

`contigpref` and `findlogstartcg` search for contiguous block ranges for UFS log placement. `findlogstartcg` uses a sliding window over cylinder-group free-block summaries to find the smallest group span that can satisfy the requested size while respecting the log extent table capacity.

Integration notes: allocation routines must pair quota reservations with physical allocation success, must not reuse blocks currently on the logging cancel list, and must update cylinder group, superblock summary, and transaction metadata together. The fallocate negative-block convention is understood by this file and by `ufs_bmap.c`.
