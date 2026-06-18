# File Research: sources/os/plan9/plan9/sys/src/9/teg2/cache-l2-pl310.c

PL310 external L2 cache driver for Tegra 2. It discovers/configures the cache, turns it on/off, and supplies range and whole-cache maintenance operations through `Cacheimpl`.

Key responsibilities:
- Maps the PL310 register layout, including control, auxiliary control, sync, invalidate/clean/clean-invalidate operations, filters, and debug register.
- Honors `*l2off` to disable L2 setup.
- Configures associativity and way size for the Tegra 2 1 MiB PL310 cache.
- Enables required auxiliary bits, especially shared-attribute override, prefetch, parity, and full-line-zero support.
- Implements range invalidate/writeback/writeback-invalidate using physical addresses and cache-line iteration.
- Implements whole-cache operations by way mask, including background-operation coordination and interrupt-level locking.
- Works around PL310 erratum 588369 by temporarily setting debug write-through/no-linefill around clean-invalidate operations.

Important behavior:
- Unaligned invalidation first cleans edge cache lines to avoid dropping dirty bytes outside the requested range.
- The code avoids lock manipulation while PL310 debug write-through mode is active because exclusive operations/locks may not work.
- Whole-cache operations may release `l2lock` while waiting only on multiprocessor systems.

Dependencies and assumptions:
- Depends on `soc.l2cache`, L1 cache helpers, `PADDR`, `CACHELINESZ`, CP15 cache setup, and Plan 9 locks.
- Assumes PL310 ID high byte is ARM when reporting cache info.

Notable risks:
- Source comments say PL310 default settings are guaranteed to work incorrectly unless `Sharovr` is set.
- Busy-wait loops wait directly on hardware operation registers.
