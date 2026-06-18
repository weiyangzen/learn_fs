# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_vnops.c

This file implements ext2fs vnode operations for metadata, creation, removal, linking, directories, symlinks, fsync, locking support, vnode initialization/reclaim, and operation vector registration.

Key responsibilities:
- Implement VOP create, mknod, open, access, getattr, setattr, remove, link, mkdir, rmdir, symlink, readlink, advlock, fsync, and reclaim.
- Enforce ext2 immutable and append-only flags.
- Translate inode fields to NetBSD `vattr` and back.
- Manage uid/gid high/low fields.
- Create inodes and install directory entries.
- Initialize special and fifo vnode operation tables.
- Register extended attribute vnode operations.

Important functions:
- `ext2fs_create` and `ext2fs_mknod`: Create new inodes with `ext2fs_makeinode`; mknod marks inode access/change/update.
- `ext2fs_open`: Rejects non-append write opens on `EXT2_APPEND` files.
- `ext2fs_check_possible`: Rejects writes to readonly regular/dir/symlink vnodes and immutable files.
- `ext2fs_check_permitted`: Calls kauth/genfs access checks against ext2 mode/uid/gid.
- `ext2fs_access`: Combines possible and permitted checks.
- `ext2fs_getattr`: Flushes pending times, exposes mode, nlink, uid/gid, rdev, size, atime/mtime/ctime, optional birthtime, ext2 flags mapped to `UF_NODUMP`, `SF_IMMUTABLE`, `SF_APPEND`, generation, blocksize, bytes, type, and filerev.
- `ext2fs_setattr`: Validates unsettable attrs; updates flags, owner/group, size, times including birthtime, and mode with readonly/immutable/append checks.
- `ext2fs_chmod` and `ext2fs_chown`: Apply authorization, update permission/ownership fields, maintain high uid/gid fields, and clear setuid/setgid when required.
- `ext2fs_remove`: Uses lookup results to remove a non-directory entry and decrement link count, rejecting immutable/append cases.
- `ext2fs_link`: Locks target, authorizes link creation, checks link max and immutable/append, increments link count, updates inode, and inserts directory entry.
- `ext2fs_mkdir`: Creates a directory inode, sets link count to 2, increments parent link count or uses `EXT2FS_LINK_INF` plus `DIR_NLINK` rocompat feature when the limit is exceeded, writes `.` and `..`, sets size to one ext2 block, and installs parent entry.
- `ext2fs_rmdir`: Rejects `.` removal, requires empty directory, enforces append/immutable, removes parent entry, adjusts link counts, truncates the directory, and purges caches.
- `ext2fs_symlink`: Creates inode and stores short symlinks inline in `e2di_shortlink`; longer symlinks are written through UFS buffer I/O.
- `ext2fs_readlink`: Reads inline symlink data when short, otherwise delegates to `UFS_BUFRD`.
- `ext2fs_advlock`: Uses `lf_advlock` with inode lockf state and ext2 size.
- `ext2fs_fsync`: Flushes vnode buffers or special device, updates inode metadata unless data-only, and optionally issues `DIOCCACHESYNC`.
- `ext2fs_vinit`: Assigns special/fifo ops, initializes device aliases, marks root vnode, and seeds inode modrev.
- `ext2fs_makeinode`: Calls `vcache_new`, locks the new vnode, optionally writes inode before directory entry, installs directory entry, and enters namecache.
- `ext2fs_reclaim`: Unlocks vnode, frees on-disk inode if `i_omode == 1` and writable, calls `ufs_reclaim`, frees ext2 dinode storage, destroys genfs node, and returns inode to pool.

Operation vectors:
- `ext2fs_vnodeop_entries`: Full regular vnode table. Uses ext2fs for lookup/create/read/write/remove/link/rename/mkdir/rmdir/symlink/readdir/readlink/inactive/reclaim/bmap/fsync/xattr operations and genfs/UFS helpers elsewhere.
- `ext2fs_specop_entries`: Special-device operations layered over `GENFS_SPECOP_ENTRIES`, with ext2fs access/getattr/setattr/fsync/inactive/reclaim/xattr.
- `ext2fs_fifoop_entries`: FIFO operations layered over `GENFS_FIFOOP_ENTRIES`, with ext2fs metadata and xattr hooks.

Important interactions:
- Uses directory helpers from `ext2fs_lookup.c`, read/write helpers from `ext2fs_readwrite.c`, rename from `ext2fs_rename.c`, xattrs from `ext2fs_xattr.c`, and shared UFS inactive/bmap/strategy/pathconf helpers.
- Creation and mutation paths rely on `VTOI(dvp)->i_crap` populated by prior lookup.
- Directory link-count overflow is represented by `EXT2FS_LINK_INF` and may set `EXT2F_ROCOMPAT_DIR_NLINK`.

Notable behavior and risks:
- `ext2fs_setattr` returns immediately after setting immutable/append flags if requested flags include `IMMUTABLE | APPEND`, preventing further attr changes in the same call.
- `ext2fs_mkdir` writes only the static `.`/`..` template size but sets directory size to the whole filesystem block.
- `ext2fs_reclaim` frees the inode pool object via `vp->v_data` after `ufs_reclaim`; correctness depends on `ufs_reclaim` not clearing or repurposing `v_data` before this point.
