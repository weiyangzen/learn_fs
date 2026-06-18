# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_extern.h

## Purpose
Declares UFS external function interfaces shared across UFS implementation files, including vnode operations, directory operations, block mapping, softdep hooks, initialization, and low-level allocation flags.

## Key Contents
- Forward declarations for UFS/VFS structures.
- VOP vectors:
  - `ufs_fifoops`
  - `ufs_vnodeops`
- Block mapping:
  - `ufs_bmap`
  - `ufs_bmaparray`
  - `ufs_bmap_seekdata`
  - `ufs_getlbns`
- Directory operations:
  - `ufs_checkpath`
  - `ufs_dirbad`
  - `ufs_dirbadentry`
  - `ufs_dirempty`
  - `ufs_makedirentry`
  - `ufs_direnter`
  - `ufs_dirremove`
  - `ufs_dirrewrite`
  - `ufs_lookup_ino`
  - `ufs_lookup`
  - `ufs_readdir`
- Extended data operations:
  - `ufs_extread`
  - `ufs_extwrite`
- Vnode lifecycle:
  - `ufs_inactive`
  - `ufs_need_inactive`
  - `ufs_reclaim`
  - `ufs_vinit`
  - `ufs_root`
- Filesystem lifecycle:
  - `ufs_init`
  - `ufs_uninit`
- Timestamp/snapshot helpers:
  - `ufs_itimes`
  - `ffs_snapgone`
- Sysctl declaration:
  - `SYSCTL_DECL(_vfs_ufs)`
- Soft updates hooks:
  - Directory add/change/remove setup.
  - Link count changes.
  - Create/link/mkdir/rmdir/unlink setup and revert.
  - `softdep_slowdown`
- Low-level allocation flags:
  - `BA_CLRBUF`
  - `BA_METAONLY`
  - `BA_UNMAPPED`
  - Sequential heuristic encoding: `BA_SEQMASK`, `BA_SEQSHIFT`, `BA_SEQMAX`

## Interactions
- Central declaration point for UFS C files.
- `ufs_bmap.c` implements several block mapping declarations here.
- Directory and vnode operation implementations elsewhere use the softdep and allocation flag contracts.
