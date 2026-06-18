# File Research: sources/os/plan9/plan9/sys/src/9/omap/cache.v7.s

Implements ARMv7/Cortex-A8 cache invalidation, writeback, and whole-cache set/way operations.

Key points:
- `cacheiinv()` invalidates the entire instruction cache and issues ISB.
- Provides small set/way primitive functions: `cachedwb_sw()`, `cachedwbinv_sw()`, and `cachedinv_sw()`.
- `setcachelvl()` and `getwayssets()` access Cortex cache-size selection and cache-size ID registers.
- `cachedwb()`, `cachedwbinv()`, and `cachedinv()` apply whole L1 data-cache operations.
- `cacheuwbinv()` atomically writebacks/invalidates data cache and invalidates I-cache with interrupts disabled.
- `l2cacheuwb()`, `l2cacheuwbinv()`, and `l2cacheuinv()` operate on the L2 cache.
- `wholecache()` computes sets/ways from CP15 cache-size registers, chooses shifts for L1 vs L2, disables interrupts, iterates all set/way combinations, calls the selected primitive, restores CPSR, and drains buffers.
- Contains a fallback `buggery` path if code runs in a zero PC segment, printing `?` to console.

Dependencies and interactions:
- Used by C helpers declared in `fns.h`, by boot/reboot code, and by MMU/cache coherency code.
- Assumes Cortex-A8 shift constants for L1 and L2 cache geometry.

Research relevance:
- Low-level cache maintenance implementation required for MMU, DMA, code patching, and reboot reliability.
