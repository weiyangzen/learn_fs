# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_vnops.c

## Purpose

`msdosfs_vnops.c` implements the FreeBSD vnode operation vector for FAT/MS-DOS files and directories. It translates VFS operations into denode, FAT-chain, directory-entry, buffer-cache, and VM pager operations while preserving FAT-specific limitations: no hard links, no symlinks, only regular files/directories, 32-bit file sizes, case-insensitive names, synthetic root dot entries, and non-sparse file data.

## Main Entry Points

- Namespace operations: `msdosfs_create()`, `msdosfs_remove()`, `msdosfs_rename()`, `msdosfs_mkdir()`, `msdosfs_rmdir()`, `msdosfs_link()`, `msdosfs_symlink()`, and `msdosfs_mknod()`.
- File state and attributes: `msdosfs_open()`, `msdosfs_close()`, `msdosfs_access()`, `msdosfs_getattr()`, `msdosfs_setattr()`, `msdosfs_fsync()`, `msdosfs_pathconf()`, and `msdosfs_print()`.
- Data and directory I/O: `msdosfs_read()`, `msdosfs_write()`, `msdosfs_readdir()`, `msdosfs_bmap()`, `msdosfs_getpages()`, and `msdosfs_strategy()`.
- Export support: `msdosfs_vptofh()` creates `struct defid` file handles from denode directory cluster/offset.
- Registration: `msdosfs_vnodeops` maps the VOP vector to these routines and inherited/common routines such as `msdosfs_lookup`, `msdosfs_inactive`, and `msdosfs_reclaim`.

## File Creation And Attribute Semantics

`msdosfs_create()` refuses to extend a full fixed root directory, creates an 8.3 on-disk name with `uniqdosname()`, initializes a zero-length archive denode with access/create/update timestamps, calls `createde()`, and populates the name cache when requested.

`msdosfs_getattr()` derives synthetic POSIX attributes from FAT metadata. The file ID computation must match `msdosfs_readdir()` so tools such as `pwd` work. Directories use their starting cluster converted to a filesystem block and directory-entry index; regular files use the containing directory cluster plus directory offset. DOS attributes map to FreeBSD user flags (`UF_ARCHIVE`, `UF_HIDDEN`, `UF_READONLY`, `UF_SYSTEM`). All objects report the mount owner/group, one link, and mode bits masked by the mount file or directory mask.

`msdosfs_setattr()` rejects unsupported vnode attributes and rejects root-directory mutation. Ownership changes are only accepted if they resolve back to the mount-wide uid/gid. Size changes are allowed only for regular files and route through `detrunc()`. Time changes use FAT timestamp conversion, skip access time when Win95 metadata is disabled, and set the archive bit for non-directories. Mode writes only affect the FAT read-only bit through the owner write bit.

## Read And Write Behavior

`msdosfs_read()` reads cluster-sized pieces until EOF or residual exhaustion. Directory data is read through the filesystem device vnode because FAT directory entry metadata lives in directory blocks and the buffer cache key must use the device vnode. Regular file reads use clustered reads unless disabled by mount flags, and set `DE_ACCESS` on successful non-read-only, non-noatime reads.

`msdosfs_write()` supports only regular files. `IO_APPEND` moves the offset to EOF. Since FAT has no sparse files, writes beyond EOF first call `deextend()` to fill the hole. Writes beyond current EOF preallocate clusters via `extendfile()` to improve contiguity. Full-cluster writes avoid disk reads by using `getblk()` and clearing the buffer first so mmap cannot observe uninitialized data if `uiomove` faults. Partial writes read existing cluster data. Buffer writeback is selected among synchronous writes, async writes under memory pressure, clustered writes on cluster boundaries, and delayed writes otherwise.

Failure handling is sensitive to `IO_UNIT`: unit writes roll file size and `uio` state back to the original state, while partial non-unit writes may return success if some data was written. `vn_rlimit_fsizex()` enforces `MSDOSFS_FILESIZE_MAX` and its result is finalized after write completion.

## Rename And Directory Operations

`msdosfs_rename()` is the most complex operation in this file. It rejects cross-device renames and unsupported flags except `AT_RENAME_NOREPLACE`, relocks source and destination parents in a deadlock-avoidance loop, revalidates source and target by on-disk directory location, rejects `.`/`..`/self-directory aliases, checks write access and hierarchy constraints for moving directories to a new parent, removes an existing compatible empty target, generates the destination DOS name, creates the destination entry, removes the old entry, updates denode hash location, and repairs a moved directory's `..` entry when its parent changes. If removing the old entry or updating `..` fails after the new entry has been written, it reports an integrity error and schedules remount read-only.

`msdosfs_mkdir()` allocates one cluster, initializes `.` and `..` entries from `dosdirtemplate`, handles FAT32 high cluster words, writes the initialized cluster before linking it from the parent, then creates the parent directory entry. On failure it frees the allocated cluster. `msdosfs_rmdir()` verifies the target directory is empty with `dosdirempty()`, removes the directory entry, purges parent and target cache entries, and truncates the directory to free its cluster chain.

Hard links, symlinks, and device nodes are unsupported (`EOPNOTSUPP` or `EINVAL`) because FAT does not represent them.

## Directory Reading

`msdosfs_readdir()` converts raw FAT directory slots into `struct dirent`. It rejects non-directories and misaligned offsets. For root directories it synthesizes `.` and `..` because FAT root directories do not store those entries in the same way as ordinary directories. It tracks long-name slots with `mbnambuf`, `win2unixfn()`, and checksum matching; if the long-name checksum fails or short-name mode is forced, it falls back to `dos2unixfn()`. Deleted, empty, long-name-only, and volume-label entries are skipped as appropriate.

The routine computes `d_fileno` consistently with `msdosfs_getattr()`, emits cookies as next FAT directory-entry offsets, sets EOF on empty slots or file-size exhaustion, and updates `uio_offset` to the last delivered FAT-entry boundary.

## Block Mapping, Pager, And Strategy

`msdosfs_bmap()` maps logical cluster numbers to device block numbers with `pcbmap()`, returns the device buffer object, and computes contiguous run lengths before and after the requested cluster for clustered I/O. It saves and restores the denode FAT-chain cache around run probing so read-ahead does not push the useful cache position too far ahead of actual I/O.

`msdosfs_getpages()` can use the buffer pager through `vfs_bio_getpages()` with FAT-specific logical block and block-size callbacks, controlled by `vfs.msdosfs.use_buf_pager`. Otherwise it falls back to `vnode_pager_generic_getpages()`.

`msdosfs_strategy()` maps unmapped buffers through `pcbmap()`, clears buffers for impossible FAT holes, sets `b_iooffset`, and dispatches to the mounted device buffer object through `BO_STRATEGY()`.

## Dependencies

The file depends on FreeBSD VFS, vnode, buffer cache, VM pager, namecache, credentials, privilege checks, resource limits, and pathconf APIs. msdosfs dependencies include denode flags and timestamps, FAT cluster allocation/free/truncation/mapping helpers, directory creation/removal helpers, DOS/Win95 name conversion, case-insensitive lookup support, and integrity-error remount support from `msdosfs_vfsops.c`.

## Invariants And Risks

- File IDs in `getattr` and `readdir` must remain identical for the same object.
- FAT directory metadata is buffer-cache keyed by the device vnode, not the directory vnode.
- FAT files cannot be sparse; extension before writes is required for holes.
- Rename has crash-consistency and corruption risk because FAT directory-entry updates are not transactional; the code remounts read-only after certain post-link failures.
- Long-name reconstruction depends on correct checksum/order handling and must gracefully fall back to 8.3 names.
- The root directory is special for FAT12/16 and partly special for FAT32, affecting dot entries, free-entry limits, and `..` encoding.
