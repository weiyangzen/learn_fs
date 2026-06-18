# File Research: sources/os/linux/linux/fs/fuse/backing.c

## Purpose
This file implements management of backing files for FUSE passthrough operations. It lets a privileged FUSE daemon register regular backing files, receive an integer backing id, look them up later, and close them.

## Main Definitions
- `fuse_backing_get()` safely increments a backing object refcount if nonzero.
- `fuse_backing_put()` frees the backing object when the refcount reaches zero.
- `fuse_backing_files_init()` initializes `fc->backing_files_map` as an IDR.
- `fuse_backing_id_alloc()` allocates cyclic ids starting at 1 under `fc->lock`.
- `fuse_backing_files_free()` destroys all registered backing files at connection teardown.
- `fuse_backing_open()` validates and registers a backing fd.
- `fuse_backing_close()` unregisters a backing id.
- `fuse_backing_lookup()` finds a backing object under RCU and returns a referenced pointer.

## Control Flow And Behavior
`fuse_backing_open()` requires passthrough support to be enabled on the connection and `CAP_SYS_ADMIN`. It rejects nonzero flags/padding, invalid fds, directories, non-regular files, and backing stack depth greater than or equal to `fc->max_stack_depth`. On success it stores the raw file pointer, prepares credentials, initializes the refcount, and inserts into the IDR.

`fuse_backing_close()` has the same capability/passthrough gate, rejects nonpositive ids, removes the object from the IDR, and drops the reference.

## Dependencies And Interfaces
The file depends on FUSE connection fields, Linux file references (`fget_raw`, `fput`), credentials (`prepare_creds`, `put_cred`), IDR, RCU, and stack-depth validation.

## Concurrency And Safety
The IDR map is protected by `fc->lock` for insert/remove. Lookup runs under RCU and uses `refcount_inc_not_zero()` to avoid resurrecting freed objects. Freeing uses `kfree_rcu()`.

## Research Notes
The TODO comments show security/observability concerns: `CAP_SYS_ADMIN` is required until backing files are visible to tools such as `lsof`, and an xarray may be reconsidered for space efficiency.
