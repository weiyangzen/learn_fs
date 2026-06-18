# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/slabhash.c

Implements a slabbed hash table: an array of independent `lruhash` tables selected by high bits of the hash.

Core behavior:
- `slabhash_create` allocates a `struct slabhash`, checks that slab count is a power of two, computes a high-bit mask/shift, and creates each underlying `lruhash` with `maxmem / numtables`.
- `slab_idx` selects a slab using `(hash & mask) >> shift`.
- Insert, lookup, remove, memory-update, and get-table operations dispatch to the selected `lruhash`.
- Delete and clear iterate all slabs.
- Status, size checks, memory accounting, traversal, entry counting, collision stats, and max-size adjustment aggregate or iterate across slabs.

Design intent:
- Unlike `lruhash`, the slab table itself does not grow.
- Multiple smaller `lruhash` tables provide multiple locks and multiple LRU lists, reducing contention.
- The slab structure is immutable after creation, so it needs no own lock for dispatch.

Test helpers:
- Defines simple test key/data structures and size/compare/delete functions to support slabhash unit tests without separate linkage to callback code.
