# File Research: sources/os/linux/linux/mm/damon/lru_sort.c

Module-style DAMON consumer that sorts LRU lists by prioritizing hot regions and deprioritizing cold regions in physical memory.

Key responsibilities:
- Exposes module parameters under `damon_lru_sort.*` for enabling, committing runtime inputs, active/inactive memory target ratio, interval autotuning, young-page filtering, hot/cold thresholds, quotas, watermarks, monitoring attributes, monitored physical range, address unit, kdamond PID, and stats.
- Builds two DAMOS schemes: `DAMOS_LRU_PRIO` for hot regions and `DAMOS_LRU_DEPRIO` for cold regions.
- Splits the configured time quota in half between hot and cold sorting schemes.
- Optionally adds quota goals for active/inactive memory ratios.
- Optionally adds young-page filters to avoid prioritizing not-young pages and avoid deprioritizing young pages.
- Selects the physical-address DAMON backend via `damon_modules_new_paddr_ctx_target()`.
- Uses `damon_set_region_biggest_system_ram_default()` when no explicit region is provided.

Runtime flow:
- `damon_lru_sort_enabled_store()` toggles the running context after DAMON initialization.
- `damon_lru_sort_apply_parameters()` builds a temporary context/schemes/target, validates parameters, then commits them into the live context with `damon_commit_ctx()`.
- Reconfiguration is handled by setting `commit_inputs`, after which the repeated `damon_call()` callback updates stats and commits new inputs inside kdamond context.
- `module_init(damon_lru_sort_init)` allocates the base paddr context and starts immediately if enabled via boot/module parameter.
