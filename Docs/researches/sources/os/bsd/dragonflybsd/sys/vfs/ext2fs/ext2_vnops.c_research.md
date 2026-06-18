# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_vnops.c

Implements ext2 vnode operations for DragonFlyBSD: file creation, open/close/access/getattr/setattr, chmod/chown, fsync, mknod, remove/link/rename, mkdir/rmdir, symlink/readlink, strategy I/O, kqueue filters, FIFO wrappers, pathconf, read, write, and vnode initialization. It registers `ext2_vnodeops`, `ext2_specops`, and `ext2_fifoops`.

`ext2_itimes` updates inode access/change/modify timestamps and marks metadata dirty. It distinguishes block/character special vnodes with `IN_LAZYMOD` and normal nodes with `IN_MODIFIED`, then clears pending timestamp flags.

Attribute paths use DragonFly VFS helpers and ext2 inode fields. `ext2_access` delegates to `vop_helper_access`. `ext2_getattr` fills `struct vattr` from `struct inode`, including nanosecond timestamps when extended inode times are available. `ext2_setattr` validates immutable attributes, handles chflags, ownership, truncation, utimes, and chmod with read-only and privilege checks.

Creation paths converge on `ext2_makeinode`, except directories use specialized setup. `ext2_create` and `ext2_mknod` allocate inodes, initialize ownership/mode/link count, write the inode before inserting the directory entry, and handle device special reload/alias behavior. `ext2_symlink` stores short symlinks inline in `i_shortlink` and long symlinks through vnode writes.

Directory mutation logic is substantial. `ext2_link` increments link count and inserts a directory entry. `ext2_rename` follows the classic UFS-style rename algorithm: bump source link, validate cross-device/sticky/append/immutable constraints, handle directory parent changes with `ext2_checkpath`, create or rewrite the target entry, remove the source entry, and patch `..` for moved directories. `ext2_mkdir` allocates a directory inode, initializes `.` and `..`, handles filetype and metadata checksum directory tails, updates parent link count, and inserts the directory entry. `ext2_rmdir` checks emptiness, removes the entry, updates parent link count, and truncates the directory inode.

`ext2_inc_nlink` and `ext2_dec_nlink` implement ext4 `DIR_NLINK` behavior. With `EXT2F_ROCOMPAT_DIR_NLINK`, directories may use link count `1` as a sentinel once the traditional limit is exceeded.

`ext2_read` and `ext2_write` implement buffered file I/O over ext2 logical blocks. Reads use `bread`, `breadn`, or `cluster_read` depending on EOF, mount flags, and sequential count; they guard against overflow and short I/O exposing bad data. Writes validate append-only semantics, file size limits, process `RLIMIT_FSIZE`, allocate blocks with `ext2_balloc`, clear buffers on failed full-block `uiomove`, choose sync/async/cluster/delayed writes, clear setuid/setgid on successful writes by unprivileged writers, and support rollback for `IO_UNIT`.

`ext2_fsync` scans dirty buffer RB trees, writes delayed buffers, waits for tracked writes when requested, and calls `ext2_update`. `ext2_strategy` maps logical offsets with `VOP_BMAP`, handles holes by clearing buffers, and forwards I/O to the underlying device vnode.

FIFO integration wraps `fifo_vnode_vops` from `fifofs`. `ext2fifo_read`, `ext2fifo_write`, `ext2fifo_close`, and `ext2fifo_kqfilter` delegate to FIFO operations while updating ext2 inode timestamps or falling back to ext2 kqueue filters.

Kqueue support defines filters for read, write, and vnode events. `ext2_kqfilter` attaches knotes to `vp->v_pollinfo`, while revoke events set EOF/NODATA/ONESHOT as appropriate.

`ext2_vinit` maps inode mode to vnode type, assigns special/fifo op tables, initializes VM objects for regular files/directories and non-inline symlinks, marks root vnode, and initializes `i_modrev`.

Important dependencies: directory functions such as `ext2_lookup`, `ext2_direnter`, `ext2_dirremove`, `ext2_dirrewrite`, `ext2_dirempty`, `ext2_checkpath`; block functions such as `ext2_balloc`, `ext2_bmap`, `ext2_truncate`; FIFO functions from `vfs/fifofs/fifo.h`.

Notable risks or research hooks: rename is complex and race-sensitive, with comments acknowledging non-atomic crash repair reliance. Directory checksum updates in rename try both dirent and htree checksum routines for block zero. Write error handling is security-relevant because it explicitly clears non-cache full-block buffers to avoid mmap exposure.
