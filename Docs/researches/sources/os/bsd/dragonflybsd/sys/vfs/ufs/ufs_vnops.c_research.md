# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_vnops.c

## Purpose

Implements the main UFS vnode operation layer: timestamps, attributes, permissions, file creation, directory operations, rename, links, symlinks, readdir/readlink, strategy I/O dispatch, FIFOs, kqueue filters, vnode initialization, inode creation, and vnode operation tables.

## Main Functional Areas

- Timestamp handling: `ufs_itimes()` updates access/change/modify times, handles 64-bit seconds split into base/ext fields, lazy special-device updates, and no-copy write timestamps.
- Creation and metadata ops: `ufs_create()`, `ufs_mknod()`, `ufs_makeinode()`, `ufs_setattr()`, `ufs_chmod()`, `ufs_chown()`.
- Link and removal ops: `ufs_link()`, `ufs_remove()`, `ufs_whiteout()`.
- Rename and directory ops: `ufs_rename()`, `ufs_mkdir()`, `ufs_rmdir()`.
- Symlink/directory reads: `ufs_symlink()`, `ufs_readdir()`, `ufs_readlink()`.
- I/O strategy and misc ops: `ufs_strategy()`, `ufs_print()`, `ufs_pathconf()`, `ufs_ioctl()`, `ufs_advlock()`.
- FIFO wrappers: `ufsfifo_read()`, `ufsfifo_write()`, `ufsfifo_close()`, `ufsfifo_kqfilter()`.
- Kqueue support: `ufs_kqfilter()`, `filt_ufsdetach()`, `filt_ufsread()`, `filt_ufswrite()`, `filt_ufsvnode()`.
- Vnode setup/dispatch: `ufs_vinit()`, `ufs_vnoperate()`, `ufs_vnoperatefifo()`, `ufs_vnoperatespec()`.

## Important Behavior

`ufs_rename()` is the most complex operation. It prevents cross-device renames, rejects unsafe directory moves, temporarily bumps source link count, checks for directory cycles with `ufs_checkpath()`, creates or rewrites the target entry, removes the old source entry with `relookup()`, and carefully unwinds locks/references on errors.

`ufs_mkdir()` manually allocates and initializes the child inode before entering it in the parent. It writes the `.` and `..` directory body first, then calls `ufs_direnter()`, with softdep-specific ordering when enabled.

`ufs_rmdir()` requires `i_effnlink == 2` and `ufs_dirempty()`, blocks removal during rename, removes the parent entry first, then truncates the directory when not using softdep.

`ufs_vinit()` selects special-device, FIFO, or regular vnode ops, creates VM objects for directories/regular files and long symlinks, sets `VROOT` for `UFS_ROOTINO`, and initializes file revision state.

## Dependencies And Integration Points

Integrates with nearly every file in this group: `ufs_lookup.c` for directory entry operations, `ufs_inode.c` for inactive/reclaim ops via vop tables, `ufs_bmap.c` through `.vop_bmap`, `ufs_quota.c` for quota checks in access/chown/makeinode/mkdir, and softdep hooks for link-count ordering.

Also calls FFS-specific helpers such as `ffs_valloc()`, `ffs_update()`, `ffs_truncate()`, and block allocation/read functions.

## Vnode Operation Tables

- `ufs_vnode_vops`: regular UFS vnode operations. Some FFS-provided operations such as read/write/fsync/reallocblks are marked with `ufs_missingop()` here.
- `ufs_spec_vops`: special-device vnode operations with UFS metadata handling.
- `ufs_fifo_vops`: FIFO vnode operations wrapping FIFO behavior while preserving UFS timestamps/attributes.

## Notes For Future Work

- Some permission checks are delegated to upper layers or helper functions; disabled historical checks remain in `#if 0`.
- Whiteout support depends on 4.4-style directory format.
- Kqueue read filters report remaining bytes from current file offset and handle revoke with EOF/NODATA flags.
- `ufs_missingop()` panics, so vnode op table wiring must ensure filesystem-specific operations override missing entries before use.
