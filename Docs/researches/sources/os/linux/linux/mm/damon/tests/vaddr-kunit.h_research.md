# File Research: sources/os/linux/linux/mm/damon/tests/vaddr-kunit.h

KUnit tests for the virtual-address DAMON backend. The header is included by `vaddr.c` under `CONFIG_DAMON_VADDR_KUNIT_TEST`, with `DAMON_MIN_REGION_SZ` forced to `1` for precise small-range expectations.

Coverage:
- Builds a synthetic VMA maple tree with `__link_vmas()`.
- Tests `__damon_va_three_regions()` on a representative mapping layout.
- Tests `damon_set_regions()` behavior when applying the three-region abstraction to existing monitoring regions.
- Covers slightly changed regions, removed subranges, moved middle regions, and fully replaced second/third regions.

Important behavior documented:
- DAMON's vaddr backend simplifies a task address space into three monitored ranges separated by the two largest unmapped gaps.
- The three resulting ranges should cover all mapped VMAs while excluding the two largest holes, which are usually heap-to-mmap and mmap-to-stack gaps.
- Applying new three-region ranges adjusts existing target region boundaries, removes regions now outside the monitored spans, and creates new regions when a monitored span appears in a different address range.

Structure:
- `damon_test_three_regions_in_vmas()` verifies the largest-gap selection and resulting three ranges for VMAs `10-25`, `200-220`, and `300-330` with the largest holes excluded.
- `damon_do_test_apply_three_regions()` sets up a target, applies three new ranges, and checks the resulting region list.
- Four apply-three-regions test cases cover progressively larger mapping changes.
- The suite name is `damon-operations`.
