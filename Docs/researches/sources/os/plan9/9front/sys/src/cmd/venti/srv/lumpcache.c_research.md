# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/lumpcache.c

`lumpcache.c` implements the in-memory cache of recently read or written lumps. It combines a 512-bucket hash table keyed by score hash/type, per-lump locks, a free list, and an eviction heap ordered by second-most-recent use.

`lookuplump()` always returns a locked `Lump`, creating or recycling a descriptor on misses, and updates usage timestamps and stats. `insertlump()` attaches packet data to a looked-up lump while enforcing byte budget by evicting idle descriptors. `putlump()` releases the per-lump lock and makes unused entries eligible for heap eviction.

The cache is concurrency-sensitive: the global cache lock protects hash/free/heap state, while the individual lump lock serializes readers/writers for the selected score. `checklumpcache()` is a debug invariant verifier for heap, hash, free-list, reference, and byte-accounting consistency.
