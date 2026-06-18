# File Research: sources/os/linux/linux/mm/damon/Kconfig

Kconfig menu for DAMON, the Data Access Monitoring framework.

Defines:
- `DAMON`: core data access monitoring framework.
- `DAMON_DEBUG_SANITY`: optional extra internal sanity checks for development/testing.
- `DAMON_KUNIT_TEST`: KUnit tests for core DAMON.
- `DAMON_VADDR`: virtual address-space monitoring operations, depends on `DAMON && MMU`, selects `PAGE_IDLE_FLAG`.
- `DAMON_PADDR`: physical address-space monitoring operations, depends on `DAMON && MMU`, selects `PAGE_IDLE_FLAG`.
- `DAMON_VADDR_KUNIT_TEST` and `DAMON_SYSFS_KUNIT_TEST`: KUnit tests for operations/sysfs pieces.
- `DAMON_SYSFS`: sysfs interface for configuring DAMON from userspace.
- `DAMON_RECLAIM`: DAMON-based proactive reclaim on physical memory.
- `DAMON_LRU_SORT`: DAMON-based LRU prioritization/deprioritization.
- `DAMON_STAT`: DAMON-based access statistics.
- `DAMON_STAT_ENABLED_DEFAULT`: default-enable knob for `DAMON_STAT`.

The file wires optional DAMON consumers to the physical-address backend where appropriate, making `DAMON_PADDR` the dependency for reclaim, LRU sorting, and stats.
