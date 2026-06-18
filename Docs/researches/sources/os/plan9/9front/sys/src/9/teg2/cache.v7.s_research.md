# File Research: sources/os/plan9/9front/sys/src/9/teg2/cache.v7.s

ARMv7 cache maintenance assembly. It implements I-cache invalidate, set/way data-cache operations, cache-level selection, whole L1/L2 writeback/invalidate wrappers, unified L1 writeback+invalidate, and the shared `wholecache` set/way iterator.

`wholecache` reads cache geometry via CP15, uses precomputed set/way shifts from `CACHECONF`, disables interrupts, runs barriers, iterates all ways and sets, and calls the selected operation stub. It includes early panic paths if cache shift parameters are invalid.

The file is intended for inclusion/use by both normal kernel code and early/reboot code where MMU mapping may be unusual.
