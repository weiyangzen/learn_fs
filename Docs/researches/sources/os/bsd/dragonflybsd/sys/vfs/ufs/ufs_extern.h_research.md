# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_extern.h

## Purpose

Declares exported UFS functions shared across the UFS/FFS implementation. It is the local interface header for vnode operations, directory helpers, inode hash helpers, VFS helpers, and softdep hooks.

## Main Declarations

- Vnode operation dispatchers: `ufs_vnoperate()`, `ufs_vnoperatefifo()`, `ufs_vnoperatespec()`.
- Block mapping: `ufs_bmap()`, `ufs_bmaparray()`, `ufs_getlbns()`.
- NFS/export helpers: `ufs_check_export()`, `ufs_fhtovp()`.
- Directory helpers: `ufs_lookup()`, `ufs_dirbad()`, `ufs_dirbadentry()`, `ufs_dirempty()`, `ufs_makedirentry()`, `ufs_direnter()`, `ufs_dirremove()`, `ufs_dirrewrite()`, `ufs_checkpath()`.
- Inode hash helpers: `ufs_ihashget()`, `ufs_ihashcheck()`, `ufs_ihashinit()`, `ufs_ihashuninit()`, `ufs_ihashins()`, `ufs_ihashlookup()`, `ufs_ihashrem()`.
- Inode lifecycle: `ufs_inactive()`, `ufs_reclaim()`.
- Generic init/root/vnode initialization: `ufs_init()`, `ufs_root()`, `ufs_start()`, `ufs_vinit()`.
- Timestamp helper: `ufs_itimes()`.
- Softdep integration hooks: directory add/change/remove setup, directory-entry offset changes, link-count changes, and slowdown check.

## Dependencies And Integration Points

Uses forward declarations rather than including the full definitions of vnode, mount, inode, directory, and credential types. Included by many files in this group to share cross-file functions.

## Notes For Future Work

- The header declares `ufs_start()` but this group does not include its implementation.
- Softdep functions are declared here even though their dependency structures are defined in `softdep.h`.
- The signatures reflect DragonFly’s older `vop_old_*` vnode operation interface.
