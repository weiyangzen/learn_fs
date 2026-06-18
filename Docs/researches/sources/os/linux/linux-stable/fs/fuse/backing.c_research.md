# File Research: sources/os/linux/linux-stable/fs/fuse/backing.c

## Purpose
Manages FUSE passthrough backing-file registrations. A privileged FUSE daemon can map operations for specific FUSE files directly to kernel backing files.

## Key Interfaces
- `fuse_backing_get()` and `fuse_backing_put()` manage `struct fuse_backing` refcounts.
- `fuse_backing_files_init()` initializes the connection IDR.
- `fuse_backing_files_free()` frees all remaining backing mappings during connection cleanup.
- `fuse_backing_open()` validates a userspace fd and allocates a backing ID.
- `fuse_backing_close()` removes a backing ID and drops its reference.
- `fuse_backing_lookup()` performs RCU-safe ID lookup and ref acquisition.

## Design Notes
Backing IDs are allocated cyclically from an IDR starting at `1`; `0` is treated as invalid. Open requires `fc->passthrough` and `CAP_SYS_ADMIN`, rejects flags/padding, requires a regular non-directory file, and prevents stack-depth loops by comparing the backing superblock depth against `fc->max_stack_depth`.

## Dependencies
Uses `struct file`, raw fd lookup, credentials, IDR, RCU, FUSE connection locking, and optional `CONFIG_FUSE_PASSTHROUGH`.

## Research Notes
A FIXME notes xarray might be space inefficient. There is also a TODO to relax `CAP_SYS_ADMIN` once backing files are visible to tools such as `lsof`.
