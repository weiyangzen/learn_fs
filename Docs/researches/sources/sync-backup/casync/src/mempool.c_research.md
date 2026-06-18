# sources/sync-backup/casync/src/mempool.c

Purpose: provides a simple fixed-size tile memory pool used through the `DEFINE_MEMPOOL` macro to amortize allocation overhead for many same-sized objects.

Important APIs/types/functions: internal `struct pool`, macro-generated `mempool_alloc_tile`, exported `mempool_free_tile`, and `mempool_drop`. A pool tracks a linked list of allocated blocks, tile size, first free tile, and allocation batch size.

Control flow/state: allocation first pops from `mp->first_free`; if empty, it allocates a new `struct pool` plus `at_least` tiles, chains all but one onto the freelist, and returns one tile. Freeing prepends the tile to the freelist. Dropping walks `first_pool` and frees every backing block.

Dependencies/integration: uses `malloc`, `free`, `offsetof`, and `util.h` helpers; consumers instantiate typed allocators in headers or C files.

Risks/test signals: tiles are not poisoned or checked for double-free, and all outstanding tile pointers become invalid after `mempool_drop`. The implementation is single-threaded and depends on correct macro-provided tile sizes.

Source research group: `subset-b-009122`.
