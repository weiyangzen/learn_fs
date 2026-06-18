# File Research: sources/os/linux/linux/mm/damon/modules-common.h

Shared declarations and module-parameter macros for DAMON module consumers.

Provides macros for:
- Monitoring attributes: `sample_interval`, `aggr_interval`, `min_nr_regions`, `max_nr_regions`.
- DAMOS time quota: `quota_ms`, `quota_reset_interval_ms`.
- DAMOS size/time quotas: adds `quota_sz`.
- Watermarks: `wmarks_interval`, `wmarks_high`, `wmarks_mid`, `wmarks_low`.
- DAMOS stats: tried/applied region counts, tried/applied bytes, and quota-exceed counts.

Also declares:
- `damon_modules_new_paddr_ctx_target()`.

The header centralizes common module parameter naming and permissions, keeping DAMON_RECLAIM and DAMON_LRU_SORT consistent.
