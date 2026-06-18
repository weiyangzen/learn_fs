# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/flush.c

This file implements public helpers for asking the PUFFS kernel side to invalidate or flush namecache and pagecache state. The shared helper `doflush` allocates a frame buffer, obtains a typed window for `struct puffs_flush`, fills the embedded request header with buffer length, `PUFFSOP_FLUSH`, and a new request id, sets operation, cookie, start, and end offsets, then enqueues it through `puffs_framev_enqueue_cc` on the current call context and selectable fd.

Public wrappers issue directory/all namecache invalidation, whole-node pagecache invalidation, ranged pagecache invalidation, whole-node pagecache flush, and ranged pagecache flush.

Integration points: depends on framebuf construction, request ids from `puffs__nextreq`, current call context lookup, and frame-vector send/yield behavior. Risks are needing a valid call context, allocation failure, and offset semantics for ranged operations.
