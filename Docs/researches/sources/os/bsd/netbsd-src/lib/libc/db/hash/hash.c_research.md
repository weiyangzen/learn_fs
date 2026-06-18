# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash.c

Implements the public `DB_HASH` access method. `__hash_open` validates access mode, opens or creates storage, initializes or reads `HASHHDR`, verifies magic/version/hash compatibility, allocates directory segments, initializes the buffer cache, and installs `DB` method pointers.

`hash_get`, `hash_put`, and `hash_delete` validate flags and permissions before calling `hash_access`. `hash_access` hashes the key to a bucket, pins the bucket chain, walks regular pairs and overflow/big-pair markers, performs get/put/delete behavior, and updates sequential-scan cursor state after deletion. `hash_seq` iterates buckets and overflow pages, returning ordinary or large key/data pairs.

Lifecycle helpers include `hash_close`, `hash_fd`, `hash_sync`, `flush_meta`, and `hdestroy`. Table growth is handled by `__expand_table`, which advances `MAX_BUCKET`, adjusts masks/spares/segments, and calls `__split_page`. `__call_hash` implements linear-hash bucket selection with high/low masks. Little-endian builds include header byte-swap helpers for big-endian on-disk order.

Dependencies include `hash_page.c` for page operations, `hash_buf.c` for buffers, `hash_bigkey.c` for large pairs, and `hash_func.c` for default hashing.

Risks/invariants: `DSIZE` reallocation appears size-sensitive and depends on historical layout expectations. Errors are recorded in `hashp->err` inconsistently across lower layers.
