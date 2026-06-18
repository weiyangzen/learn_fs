# File Research: sources/local-fs/squashfs-tools/squashfs-tools/caches-queues-lists.h

Header for the mksquashfs queue/cache subsystem.

Defines macro generators:
- `INSERT_LIST` / `REMOVE_LIST` for circular doubly-linked freelists.
- `INSERT_HASH_TABLE` / `REMOVE_HASH_TABLE` for doubly-linked hash buckets.

Core constants:
- `HASH_SIZE` 65536 and `CALCULATE_HASH`.
- Next-state values: `NEXT_BLOCK`, `NEXT_FILE`, `NEXT_VERSION`.
- Buffer source/type values: `QUEUE_CACHE`, `GEN_CACHE`, `WSYNC_CMD`, `RESET_CMD`, `MAP_CMD`.

Defines all queue/cache structs:
- `file_buffer`: central buffer envelope carrying index, sequence/file/block ordering, data size, compressed byte count, checksum, flags, ownership pointers, list/hash links, and inline aligned data.
- `queue`, `seq_queue`, `readq_thrd`, `read_queue`, `cache`, `writeq_thrd`, `queue_cache`.

Exports the queue/cache API implemented in `caches-queues-lists.c`.

Inline helpers:
- `gen_cache_block_put()` dispatches release by buffer type.
- `cache_maxsize()` returns the owning cache capacity.
- `is_sparse()`, `set_sparse()`, and `sparse_count()` encode sparse extents using negative `c_byte`.

Notable risks/quirks:
- `cache_maxsize()` has fatal error paths in an `int` inline function with no return after `BAD_ERROR()`.
- Sparse length is limited to `INT_MAX`.
