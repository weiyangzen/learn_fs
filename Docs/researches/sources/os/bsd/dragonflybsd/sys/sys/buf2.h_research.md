# File Research: sources/os/bsd/dragonflybsd/sys/sys/buf2.h

Read completely: 392 lines.

This kernel header provides inline helpers for buffer locks, BIO queues, buffer activity, dependency callbacks, completion chaining, and common read wrappers.

Key contents:
- `BUF_LOCKINIT`, `BUF_LOCK`, `BUF_TIMELOCK`, `BUF_UNLOCK`, `BUF_KERNPROC`, `BUF_LOCKINUSE`, and `BUF_LOCKFREE`.
- BIO queue helpers for init, insert, remove, first, and take-first.
- Buffer activity advance/decline helpers.
- `buf_dep_init`, dependency count/deallocate/start/complete/fsync/move/check callbacks via `bio_ops`.
- `biodone_chain()` for chained BIO completion.
- Inline wrappers for `bread`, `bread_kvabio`, `breadn`, `cluster_read`, and `cluster_read_kvabio`.

Important interactions:
- Depends on `buf.h`, mount/vnode headers, and VM page constants.
- Some dependency callbacks force `bkvasync_all()` if the vnode does not support KVABIO.

Security/reliability notes:
- Lock helpers mutate lock wait message/timeout fields, with comments noting benign races.
- Dependency callbacks run in sensitive flush paths and must preserve KVA coherency before filesystem callbacks.
