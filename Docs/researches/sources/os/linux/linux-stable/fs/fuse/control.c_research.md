# File Research: sources/os/linux/linux-stable/fs/fuse/control.c

## Purpose
Implements the `fusectl` pseudo-filesystem exposing per-connection control and monitoring files.

## Key Interfaces
- `fuse_ctl_add_conn()` creates a directory named by connection device ID with files `waiting`, `abort`, `max_background`, and `congestion_threshold`.
- `fuse_ctl_remove_conn()` removes a connection directory.
- `fuse_conn_abort_write()` aborts a connection when userspace writes to `abort`.
- `fuse_conn_waiting_read()` reports pending request count.
- Limit read/write helpers expose and update `max_background` and `congestion_threshold`.
- `fuse_ctl_init()` and `fuse_ctl_cleanup()` register/unregister the `fusectl` filesystem.

## Design Notes
A single global `fuse_control_sb` exists while `fusectl` is mounted and is protected by `fuse_mutex`. Control dentries use persistent simplefs-style dentries and store `struct fuse_conn *` in `inode->i_private`. Accessors take a connection reference under `fuse_mutex`.

## Dependencies
Uses simple filesystem helpers, FUSE global connection list, `fuse_mutex`, VFS fs_context operations, capability checks, and FUSE background throttling fields.

## Research Notes
Non-privileged writes to limits are capped by global user limits, while privileged callers can set up to the 16-bit maximum. Updating `max_background` also recomputes blocked state and wakes blocked waiters if capacity opens.
