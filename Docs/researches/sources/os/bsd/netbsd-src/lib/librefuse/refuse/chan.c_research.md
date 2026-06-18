# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/chan.c

This file implements ReFUSE's internal emulation of the old FUSE channel API. A `struct fuse_chan` stores mountpoint, copied args, associated `struct fuse`, and a deferred-destroy flag. A global expandable vector stores channels by integer index so old APIs that return "fds" can return a small handle.

The API creates/destroys channels, stashes/peeks/takes/finds them, sets associated fuse state, and exposes mountpoint/args/fuse/destroy-pending accessors. Optional pthread locking protects the global storage.

Risks: the storage can leak by design if old callers destroy without later unmounting, and `realloc` failure after assigning `storage.vec` would lose the old vector pointer. Semantics are only an approximation of Linux FUSE channels.
