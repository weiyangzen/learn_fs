# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_itimes.c

## Purpose

`lfs_itimes.c` implements `lfs_itimes()`, the shared timestamp update helper for LFS inodes. It updates dinode access, modification, and change times, mirrors access time into the Ifile for newer formats, marks inodes/Ifile dirty, updates `i_modrev`, and clears pending timestamp request flags.

## Behavior

`lfs_itimes(ip, acc, mod, cre)` requires one of `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, or `IN_MODIFY`. In kernel builds it obtains `now` with `vfs_timestamp()` when the caller does not provide explicit times.

For `IN_ACCESS`, it updates dinode atime fields. On 64-bit or post-v1 filesystems, it also updates the Ifile entry's atime fields, taking `lfs_fraglock` when the segment lock is not already held, writes the Ifile entry, and marks `LFS_IFDIRTY`. On older formats it marks the inode `IN_ACCESSED`.

For `IN_UPDATE` or `IN_MODIFY`, it updates mtime and increments `i_modrev`. For `IN_CHANGE` or `IN_MODIFY`, it updates ctime. It then marks `IN_MODIFIED` or `IN_ACCESSED` as appropriate under `lfs_lock`.

## Integration Notes

This helper is used by inode writeback and update paths so timestamp propagation is centralized. It supports both kernel and userland LFS tool builds by remapping kernel buffer/vnode/panic names in non-kernel mode.
