# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_vnops.c

## Purpose

`bootfs_vnops.c` implements vnode operations for bootfs directories and regular files. It serves directory traversal, reads, attributes, access checks, page faults, and mmap for boot-time module contents.

## File Shape

- Size: 547 lines, 12,107 bytes.
- SHA-256: `f0196775f50b471c8139459d05002510edd3d2a61224b78767726a66a37c5adc`.
- Defines `bootfs_vnodeops` and `bootfs_vnodeops_template`.
- Key vnode ops: `bootfs_read()`, `bootfs_getattr()`, `bootfs_access()`, `bootfs_lookup()`, `bootfs_readdir()`, `bootfs_getpage()`, `bootfs_map()`, and `bootfs_pathconf()`.

## Core Behavior

- `bootfs_read()` rejects directories/non-regular nodes and negative offsets, reads only up to EOF, uses segmap to fault pages, copies data with `uiomove()`, releases segmap, and updates access time.
- `bootfs_getattr()` returns the node's stored `vattr_t` while preserving the caller's requested mask.
- `bootfs_access()` applies ordinary vnode access policy against stored uid/gid/mode.
- `bootfs_lookup()` supports `.`, `..`, rejects xattr lookup, requires a directory, and finds children in the parent AVL tree by name.
- `bootfs_readdir()` emits `.` and `..`, then AVL-ordered children. Directory offsets are based on name lengths, with `.` at 0, `..` at 1, and real entries starting at 3.
- `bootfs_rwlock()` rejects write locks; bootfs is immutable.
- `bootfs_seek()` validates regular-file offsets against file size and always allows directory seek.
- `bootfs_getapage()` creates or looks up a page for the vnode offset, locates the source physical page from `bvn_addr + off`, copies it into the vnode page with `ppcopy()`, and returns it through page-list plumbing.
- `bootfs_getpage()` handles single-page or multi-page requests via `bootfs_getapage()`/`pvn_getpages()`, and permits reads up to file size plus page offset.
- `bootfs_map()` supports private mappings of regular files through `segvn_create`, rejects writable shared mappings, invalid offsets, non-regular vnodes, and `VNOMAP`.
- `bootfs_pathconf()` reports timestamp resolution of 1 and delegates other queries to `fs_pathconf()`.

## Dependencies And Contracts

- Depends on physical-memory page copying (`page_numtopp_nolock()`, `ppcopy()`), segmap, segvn, and VM page-list helpers.
- Directory lookup and readdir depend on AVL ordering established in `bootfs_construct.c`.
- Read and mmap semantics assume boot module memory remains valid for the lifetime of the mounted bootfs.

## Maintenance Notes

This vnode implementation is immutable: no create/remove/write/setattr operations are exposed. Page-fault code copies from physical pages instead of using a normal backing store; changes to boot module address representation or lifetime must update `bootfs_getapage()`.
