# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_vnops.c

Read completely: 896 lines.

Implements EFS vnode operations. Lookup checks execute permission, consults the name cache, handles `.`, searches directory extents with `efs_inode_lookup()`, returns `EJUSTRETURN` only for impossible write/create style paths after access checks, and caches positive or negative results.

Access uses kauth/genfs with inode uid/gid/mode and rejects writes on read-only mounts. Getattr exposes inode metadata, block size, times, generation, and decodes old or new EFS special-device numbers for `va_rdev`.

Regular file reads walk extents and use UBC to transfer ranges that overlap the current extent. Readdir walks directory extents and directory-block slots, validates magic and slot offsets, creates `dirent` records, and reads each target inode to determine `d_type`. Readlink supports inline symlinks stored in the inode union and symlink data stored in extents, returning a NUL-terminated buffer through `uiomove()`.

`efs_bmap()` maps logical EFS basic blocks through the extent iterator and reports run length. `efs_strategy()` resolves logical blocks then forwards I/O to the mounted device. The vnode op tables are read-only for namespace and file modification, while special and FIFO tables pass through appropriate genfs/spec/fifo operations.
