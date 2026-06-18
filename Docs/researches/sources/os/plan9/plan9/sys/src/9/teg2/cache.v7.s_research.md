# File Research: sources/os/plan9/plan9/sys/src/9/teg2/cache.v7.s

ARMv7 assembly cache-maintenance routines for instruction cache invalidation, L1 data/unified cache operations, optional architectural L2 operations, and set/way traversal.

Key responsibilities:
- Provides `cacheiinv`, `cachedwb`, `cachedwbinv`, `cachedinv`, and `cacheuwbinv`.
- Provides single set/way primitives for clean, clean-invalidate, and invalidate.
- Provides `setcachelvl` and `getwayssets` CP15 cache-size helpers.
- Provides architectural L2 routines `_l2cacheuwb`, `_l2cacheuwbinv`, and `_l2cacheuinv`.
- Implements `wholecache`, which reads selected cache geometry, derives ways/sets, uses shift values from low memory `CACHECONF`, and iterates every set/way.
- Handles early-MMU cases by mapping function and data pointers into the caller's current segment.

Important behavior:
- Whole-cache operations run with interrupts disabled and end with barrier sequences.
- If cache geometry shift values are zero, the code prints a short early-console diagnostic and panics with `bad cache params`.

Dependencies and assumptions:
- Depends on `arm.s`, `arm.h`, low-memory `Lowmemcache` layout, and CP15 cache-size registers.
- Assumes cache line geometry has already been recorded in `CACHECONF` before set/way whole-cache operations are needed.

Notable risks:
- The assembly is tightly coupled to register use by Plan 9's external-register convention (`R9`/`R10`) and to `CACHECONF` offsets.
- Direct set/way operations are sensitive to correct cache-level selection and shift values.
