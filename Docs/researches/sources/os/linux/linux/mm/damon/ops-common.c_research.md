# File Research: sources/os/linux/linux/mm/damon/ops-common.c

Shared low-level helpers for DAMON address-space operation backends.

Key responsibilities:
- Safely obtains LRU folios from PFNs with `damon_get_folio()`.
- Clears young/accessed state for PTEs/PMDs while interacting with MMU notifiers and folio idle state.
- Walks reverse mappings to mark folios old (`damon_folio_mkold()`) or test whether folios are young (`damon_folio_young()`).
- Computes hot and cold DAMOS scores from access frequency and region age.
- Implements folio-level DAMOS ops filters for anon, active, memcg, young, hugepage-size, and unmapped filters.
- Migrates folio lists to a target NUMA node for DAMOS migration actions.
- Provides `damos_ops_has_filter()`.

Important details:
- Device-exclusive/PFN swap entries that map pages are treated as CPU-old, with MMU notifier handling device-side young state.
- Young filter matching can also clear young state by calling `damon_folio_mkold()`.
- Migration uses `MIGRATE_ASYNC`, `MR_DAMON`, `GFP_NOWAIT`, and ignores cpuset/mempolicy constraints.
- Folios that fail migration are put back on the LRU.
