# File Research: sources/os/plan9/plan9/sys/src/9/teg2/caches-v7.c

ARMv7 cache-geometry discovery and diagnostic printing.

Key responsibilities:
- Reads CP15 cache-level and cache-size registers to fill `Memcache` descriptors.
- Supports external L2 reporting by delegating level-2 information to `allcache->info`.
- Computes line length, number of sets, number of ways, set shift, and way shift.
- Prints cache configuration, write policy capabilities, and L1 instruction-cache indexing policy.

Dependencies and assumptions:
- Depends on `cprdsc`, `cpwrsc`, `cpctget`, `log2`, `cachel`, and `allcache`.
- Uses ARMv7 CLIDR/CCSIDR-style fields and Cortex cache-type encodings.

Notable risks:
- `allcacheinfo` currently iterates architectural cache levels and has the external PL310 line commented out, so external L2 reporting depends on other initialization paths.
