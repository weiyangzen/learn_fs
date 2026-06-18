# File Research: sources/os/linux/linux/mm/damon/paddr.c

Physical address-space DAMON operations backend.

Key responsibilities:
- Converts between DAMON core addresses and physical addresses using `ctx->addr_unit`.
- Prepares access checks by selecting a random sampling address per region and marking the corresponding folio old.
- Checks accesses by testing folio young/idle state and updating region access rates.
- Registers `DAMON_OPS_PADDR` at subsys init.
- Applies physical-memory DAMOS actions: pageout, LRU prioritize, LRU deprioritize, hot/cold migration, and stats.
- Scores schemes using hot/cold score helpers from `ops-common.c`.

DAMOS behavior:
- `damon_pa_pageout()` iterates folios in a region, installs a young-page reject filter by default if none exists, isolates reclaimable folios, and calls `reclaim_pages()`.
- `damon_pa_de_activate()` activates or deactivates folios for LRU priority changes.
- `damon_pa_migrate()` isolates folios and migrates them to the scheme’s target node.
- `damon_pa_stat()` only counts bytes passing ops filters.
- `last_applied` avoids repeatedly applying an action to the same folio when regions overlap folio boundaries.

Filtering:
- Core filters are respected before ops filters via `scheme->core_filters_allowed`.
- Ops filters are evaluated with `damos_folio_filter_match()`.
- `sz_filter_passed` is accumulated in core-address units, matching DAMON’s address-unit scaling.
