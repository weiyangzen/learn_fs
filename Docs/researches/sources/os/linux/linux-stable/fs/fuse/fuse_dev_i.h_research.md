# File Research: sources/os/linux/linux-stable/fs/fuse/fuse_dev_i.h

## Purpose

`fuse_dev_i.h` is an internal header for FUSE device-side request transport. It declares request-ID conventions, `/dev/fuse` device helpers, copy-state tracking, and internal functions used by the FUSE device implementation.

## Main Responsibilities

- Defines request ID layout:
  - ordinary requests use even unique IDs,
  - interrupt requests use the low bit via `FUSE_INT_REQ_BIT`,
  - normal request IDs advance by `FUSE_REQ_ID_STEP`.
- Declares the global `fuse_dev_waitq` used for device/mount coordination.
- Defines `struct fuse_copy_state`, the state used when copying request payloads between kernel request buffers and userspace/device iterators or pipes.
- Provides safe inline accessors for `struct fuse_dev` from a file and for reading `fud->fc`.
- Declares request lookup, queue, interrupt, forget, copy, and timeout helpers implemented elsewhere.

## Key Types

`struct fuse_copy_state` tracks:
- Current request.
- I/O iterator.
- Pipe buffers and current pipe buffer.
- Current page, length, and offset.
- Direction (`write`), folio movement, io_uring mode, and ring-copy accounting.

`FUSE_DEV_FC_DISCONNECTED` is a sentinel stored in `fud->fc` after `/dev/fuse` is closed.

## Concurrency Notes

`fuse_dev_fc_get()` uses `smp_load_acquire()` and pairs with `xchg()`/`cmpxchg()` in device install/release paths. The comments document when lockless dereference is safe and where exceptions exist.

## Dependencies

This header depends on `struct fuse_conn`, `struct fuse_dev`, request queue structures, and the FUSE device implementation. It is included by `inode.c` and device-side code.
