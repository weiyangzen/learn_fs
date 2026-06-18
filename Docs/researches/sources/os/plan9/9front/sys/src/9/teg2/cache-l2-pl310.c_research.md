# File Research: sources/os/plan9/9front/sys/src/9/teg2/cache-l2-pl310.c

Implements Tegra 2’s external PL310 L2 cache as a `Cacheimpl`. It configures ways/sets, enables PL310 with required auxiliary bits, and provides whole-cache and range operations for invalidate, writeback, and writeback+invalidate.

The code documents two critical hardware issues: shared-attribute override must be set for correctness, and clean+invalidate needs an erratum 588369 workaround by temporarily forcing write-through/no-line-fill in the debug register.

Range invalidation cleans unaligned boundary lines first. Whole-cache operations use way masks and a `bg_op_running` flag with lock coordination, optionally releasing the lock while polling on SMP.
