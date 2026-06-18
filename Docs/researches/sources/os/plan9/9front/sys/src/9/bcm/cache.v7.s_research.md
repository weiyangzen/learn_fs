# File Research: sources/os/plan9/9front/sys/src/9/bcm/cache.v7.s

Cortex/ARMv7 cache-maintenance implementation shared by normal and reboot assembly.

Key behavior:
- Invalidates all instruction cache and branch predictor, or an instruction-cache range.
- Provides set/way data cache operators for clean, invalidate, and clean+invalidate.
- Provides whole L1 and L2 cache operations using selected cache level and CCSIDR-style set/way counts.
- Wraps unified clean+invalidate with interrupt masking.
- Computes set/way register contents in a hand-translated loop.

Dependencies:
- Included by `armv7.s` and reused by reboot code.
- Uses ARM CP15 cache-size select/register operations.

Research notes:
- Whole-cache functions can execute before MMU is on by remapping function pointers into the current PC segment.
