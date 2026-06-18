# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_main.c

Initializes and tears down the FS-Cache subsystem embedded in netfs support.

Key behavior:
- Creates the global `fscache` workqueue.
- Initializes proc entries through `fscache_proc_init()`.
- Creates the `fscache_cookie_jar` slab cache.
- Exports FS-Cache tracepoints and `fscache_wq`.
- Provides an architecture-independent 32-bit hash function derived from `full_name_hash()` but stable for on-disk use.
- Teardown destroys the cookie slab, proc entries, LRU timer, and workqueue.
