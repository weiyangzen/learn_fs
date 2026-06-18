# File Research: sources/os/plan9/9front/sys/src/9/teg2/caches-v7.c

Discovers and reports ARMv7 cache geometry. `cacheinfo` fills `Memcache` for a given level, using CP15 cache-size registers for internal caches and `allcache->info` for external L2. `allcacheinfo` walks cache-level ID fields. `prcachecfg` prints cache level, type, ways, sets, line size, write capabilities, and L1 I-cache indexing policy.

This file supplies metadata used by low-level cache assembly and diagnostics; it does not perform maintenance operations itself.
