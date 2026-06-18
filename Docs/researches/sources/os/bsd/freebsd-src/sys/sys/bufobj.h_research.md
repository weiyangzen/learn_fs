# File Research: sources/os/bsd/freebsd-src/sys/sys/bufobj.h

## Purpose
`bufobj.h` defines the buffer object abstraction that owns clean and dirty buffers independently of vnodes.

## Main Interfaces
- `struct bufv` combines a TAILQ sorted block list, a pctrie root, and a buffer count.
- `struct buf_ops` supplies write, strategy, sync, and delayed-flush operations.
- `struct bufobj` contains an rwlock, operation vector, VM object pointer, syncer list link, private data, clean and dirty buffer sets, output count, flags, domain, and block size.
- Macros dispatch `BO_STRATEGY`, `BO_SYNC`, `BO_WRITE`, and `BO_BDFLUSH`.
- Lock macros wrap the bufobj rwlock.
- Functions initialize, reference/drop write activity, invalidate buffers, wait for writes, sync, and background flush.

## Implementation Notes
The architectural comment explains why buffer cache ownership moved from vnodes to `bufobj`: GEOM and other non-vnode code also need buffer-cache integration.

## Dependencies and Constraints
Visible for `_KERNEL` or `_KVM_VNODE`. Locking comments mark constant fields, vnode-protected fields, and sync-mutex-protected fields. `BO_DEAD` is intended for invariant checking.
