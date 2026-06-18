# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_hash.c

## Purpose

This file owns initialization and destruction of MDCACHE's file-handle lookup table. The table maps hashed lower-FSAL handle keys to `mdcache_entry_t` objects using partitioned AVL trees plus a direct cache slot array. The source was read as a complete 114-line file.

## Important APIs, Types, and Functions

Important symbols are global `struct cih_lookup_table cih_fhcache`, static `initialized`, `cih_pkginit`, and `cih_pkgdestroy`.

## Control Flow

Initialization reads `mdcache_param.nparts` and `mdcache_param.cache_size`, allocates the partition array, initializes each partition mutex and AVL tree with `cih_fh_cmpf`, and allocates the per-partition cache slot array. Destroy iterates partitions, logs if any AVL tree is not empty, destroys mutexes, frees cache arrays and the partition table, and clears the initialized flag.

## State and Persistence Behavior

All state is process memory. Partitions contain locks, AVL trees, and cache slots. No file-backed persistence exists; cache contents must be empty or intentionally torn down before package destruction.

## Dependencies and Integration Points

It depends on `mdcache_param`, `mdcache_hash.h`, `mdcache_int.h`, AVL support, and Ganesha allocation/logging. Inline lookup/insert/remove functions in `mdcache_hash.h` operate on the global table initialized here.

## Risks and Edge Cases

Destroy only logs non-empty trees, so callers must ensure cache cleanup happens before package shutdown. A zero or poor `nparts`/`cache_size` configuration would break partition/cache modulo assumptions. Partition lock destruction while entries remain can race if shutdown order is wrong.

## Test Signals

Initialize/destroy with representative partition/cache sizes, check mutex and allocation cleanup under leak tools, verify warnings for non-empty trees in controlled tests, and run concurrent locate/insert/remove stress after init.
