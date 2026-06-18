# File Research: sources/os/plan9/9front/sys/src/9/omap/l.s

Primary OMAP ARM kernel assembly startup and low-level CPU primitives.

Key behavior:
- `_start` builds early section mappings, sets up kernel stack and SB, enables MMU/caches, clears BSS, initializes `Mach`, and calls kernel `main`.
- `_reset` provides a reset entry path.
- `_r15warp` adjusts execution across address segments during MMU transitions.
- Exports range cache operations: `cachedwbse`, `cachedwbinvse`, and `cachedinvse`.
- Exports MMU helpers: enable, disable, invalidate all, invalidate address.
- Exports CP15 accessors for CPU ID, cache type, control, TTB, DAC, FSR/IFSR/FAR, PID, SCR, and PSR.
- Implements interrupt priority helpers `splhi`, `spllo`, `splx`, `islo`.
- Implements TAS, CLZ, labels, caller-PC fetch, `idlehands`, and `coherence`.
- Includes `cache.v7.s` for full cache operations.

Research notes:
- Startup emits serial “wave” characters for very early diagnostics.
- The loader uses R11 as scratch, and comments/macros account for that.
