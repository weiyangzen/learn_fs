# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_cdir.c

## Purpose

`ctfs_cdir.c` implements per-contract directories under `/system/contract/<type>/<ctid>`. Each such directory contains `ctl`, `status`, and `events` entries for operating on that contract.

## File Shape

- Size: 165 lines, 4,488 bytes.
- SHA-256: `dc2665cd2eecf5af7af5a118231ea047ac5f5b05a38c8ba78a58331d52570cad`.
- Public creator: `ctfs_create_cdirnode()`.
- Operation vector: `ctfs_tops_cdir`.

## Core Behavior

- Defines static GFS entries: `ctl`, `status`, and `events`.
- `ctfs_create_cdirnode()` first checks whether the contract already has a vnode for the target VFS. If not, it creates a GFS directory, assigns its contract-directory inode, holds the contract, and links the vnode into the contract's vnode list.
- `ctfs_cdir_getattr()` reports a read-only directory with link/size count covering `.`/`..` plus the three control entries; ctime comes from contract creation time, and atime/mtime come from the contract event queue.
- `ctfs_cdir_do_inode()` derives child file inode numbers from the contract ID and static child index.
- `ctfs_cdir_inactive()` removes the directory vnode from the contract's vnode list, releases the contract, and frees private node data once GFS says the directory is inactive.

## Dependencies And Contracts

- Relies on `contract_vnode_get()`/`contract_vnode_set()` for per-contract vnode caching.
- Child nodes are created by `ctfs_create_ctlnode()`, `ctfs_create_statnode()`, and `ctfs_create_evnode()`.

## Maintenance Notes

The cdir vnode transitively holds the contract for its child files. Inactive ordering matters: the vnode must be removed from `ct_vnodes` while holding `ct_lock`, then the contract reference can be dropped.
