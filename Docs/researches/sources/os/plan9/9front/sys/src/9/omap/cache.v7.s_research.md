# File Research: sources/os/plan9/9front/sys/src/9/omap/cache.v7.s

ARMv7/Cortex-A8 cache-maintenance routines.

Key behavior:
- Exports instruction-cache invalidate, data-cache clean, invalidate, and clean+invalidate operations.
- Provides single set/way CP15 cache operators plus whole L1/L2 cache traversal.
- `cacheuwbinv` disables interrupts, cleans/invalidates data cache, and invalidates I-cache.
- L2 wrappers select level 2 and reuse the shared whole-cache loop.
- `wholecache` reads cache geometry from CP15, computes way/set encodings, and iterates all sets and ways.

Research notes:
- Whole-cache traversal remaps function pointers into the current PC segment so it can run during MMU transition windows.
- The set/way shifts are hard-coded for Cortex-A8 cache geometry.
