# File Research: sources/os/plan9/9front/sys/src/9/arm64/cache.v8.s

ARMv8 cache-maintenance assembly for instruction/data cache ranges and whole-cache operations.

Key behavior:
- Provides instruction cache invalidation by range and all-cache invalidation.
- Provides data cache clean, clean-to-PoU, invalidate, and clean+invalidate by virtual address range.
- Provides whole L1 and L2 set/way cache operations.
- Computes line size, set count, and way count from `CCSIDR_EL1` after selecting cache level with `CSSELR_EL1`.
- Masks interrupts around cache-size selection and maintenance loops, then restores `DAIF`.

Dependencies:
- Uses ARM64 system register encodings from `sysreg.h`.
- Called by MMU, reboot, DMA, and text-flush paths.

Research notes:
- Range operations align start/end addresses to discovered cache line size.
- Whole-cache operations use set/way iteration and barriers to make state globally visible.
