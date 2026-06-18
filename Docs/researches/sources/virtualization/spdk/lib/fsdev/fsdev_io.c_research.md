# File Research: sources/virtualization/spdk/lib/fsdev/fsdev_io.c

## Purpose
Implements public fsdev operation wrappers. Each API allocates and fills an `spdk_fsdev_io`, sets operation-specific input fields, submits it to the fsdev module, adapts module completion to a typed user callback, and frees temporary resources.

## Operation Pattern
- `fsdev_io_get_and_fill()` obtains an IO from the channel cache/mempool and initializes common fields: fsdev, channel, descriptor, type, unique ID, user callback, internal callback, default `-ENOSYS` status, and submit flag.
- Each `spdk_fsdev_*()` function fills `u_in.<operation>` and calls `fsdev_io_submit()`.
- Each `_spdk_fsdev_*_cb()` pulls results from `u_out.<operation>`, invokes the typed user callback via `CALL_USR_CLB` or `CALL_USR_NO_STATUS_CLB`, releases any strdup/malloc data, and returns the IO to the pool.

## Covered Operations
Implements wrappers for mount, umount, lookup, forget, getattr, setattr, readlink, symlink, mknod, mkdir, unlink, rmdir, rename, link, open, read, write, statfs, release, fsync, xattr set/get/list/remove, flush, opendir, readdir, releasedir, fsyncdir, flock, create, abort, fallocate, and copy-file-range.

## Resource Ownership
- Copies string inputs for path/name/xattr fields using `strdup()` and releases them in completion callbacks.
- Copies xattr values into owned malloc memory for `setxattr`.
- Read/write buffers and iovecs are caller-owned and passed through.
- `readlink` expects module output `linkname` to be heap-owned and frees it after callback.
- `readdir` uses a module entry callback shim to invoke the user entry callback for each output entry.

## Notes
There is a likely typo in `spdk_fsdev_symlink()`: after `u_in.symlink.linkpath = strdup(linkpath)`, the failure check tests `if (!fsdev_io)` instead of `if (!fsdev_io->u_in.symlink.linkpath)`. That would miss allocation failure and then dereference/free through a bad state.
