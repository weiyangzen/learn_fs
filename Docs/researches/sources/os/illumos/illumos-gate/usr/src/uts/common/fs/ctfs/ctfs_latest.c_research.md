# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_latest.c

## Purpose

`ctfs_latest.c` implements the `/system/contract/<type>/latest` pseudo-file. It acts as a doorway to the `status` file for the current LWP's latest contract of that type.

## File Shape

- Size: 183 lines, 4,218 bytes.
- SHA-256: `3f05dc4acecb06dd3859fe6524758f57756ea8bcc8576a165a90b73661278d3e`.
- Public creator: `ctfs_create_latenode()`.
- Operation vector: `ctfs_tops_latest`.

## Core Behavior

- `ctfs_latest_nested_open()` indexes `ttolwp(curthread)->lwp_ct_latest` by the parent type directory index. If a latest contract exists, it creates/gets that contract's cdir vnode, looks up its `status` child, releases the cdir vnode, and returns the held status vnode.
- `ctfs_latest_access()` denies write/execute, then succeeds only when a latest contract status vnode can be opened.
- `ctfs_latest_open()` requires `FREAD | FOFFMAX`, replaces the latest vnode with the nested status vnode, and opens that status vnode.
- `ctfs_latest_getattr()` forwards getattr to the nested status vnode when one exists; otherwise it returns bland read-only regular-file attributes with mount-time timestamps.
- Close, ioctl, readdir, and lookup are invalid/not-directory operations for the latest vnode itself.

## Dependencies And Contracts

- Relies on per-LWP latest-contract tracking and parent GFS file index matching contract type index.
- Uses `ctfs_create_cdirnode()` and GFS lookup of `status`.

## Maintenance Notes

`latest` is intentionally not a normal status file; it is a dynamic indirection based on the calling LWP. Open replaces the vnode pointer with the real status vnode, which is important for callers expecting to use normal status ioctls afterward.
