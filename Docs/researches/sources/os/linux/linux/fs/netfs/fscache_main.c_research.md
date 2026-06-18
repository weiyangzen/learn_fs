# File Research: sources/os/linux/linux/fs/netfs/fscache_main.c

Initializes and tears down the FS-Cache component of netfs support.

Key responsibilities:
- Defines and exports `fscache_wq`.
- Exports FS-Cache tracepoints.
- Provides stable architecture-independent hash function for cache keys.
- Initializes `/proc` entries and cookie slab cache.
- Destroys FS-Cache resources at module exit.

Important APIs:
- `fscache_hash()`: hashes little-endian 32-bit chunks with fixed mixing.
- `fscache_init()`: allocates workqueue, initializes proc entries, creates cookie slab.
- `fscache_exit()`: destroys cookie slab, proc entries, LRU timer, and workqueue.

Notable details:
- Hash function is intentionally architecture-independent because hash bits may be persisted on disk.
- Caller must provide data length rounded to a multiple of four bytes.
