# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/legacy.c

This file implements the removed legacy `fuse_invalidate` API in terms of modern `fuse_invalidate_path`. It treats `-ENOENT` as non-error because there was no cache entry to invalidate.

Integration points: paired with `legacy.h` and `refuse.c`'s no-cache `fuse_invalidate_path` implementation. Risk is semantic mismatch: ReFUSE does not currently cache paths, so invalidation is effectively a compatibility no-op.
