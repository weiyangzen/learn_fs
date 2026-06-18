# File Research: sources/os/linux/linux/mm/damon/reclaim.c

Module-style DAMON consumer for proactive reclamation of cold physical memory.

Key responsibilities:
- Exposes `damon_reclaim.*` module parameters for enable/disable, runtime input commit, cold age threshold, quotas, PSI/user-feedback quota goals, watermarks, monitoring intervals, monitored physical range, address unit, anon-skip filter, stats, and kdamond PID.
- Builds a single `DAMOS_PAGEOUT` scheme targeting regions of at least `PAGE_SIZE`, with zero accesses and age at least `min_age / aggr_interval`.
- Defaults quota to 10 ms and 128 MiB per second.
- Uses free-memory watermarks to activate/deactivate reclaim work.
- Optionally adds a PSI-based quota goal and/or user-feedback quota goal.
- Optionally adds an anon-page reject filter when `skip_anon` is true.

Runtime flow:
- `damon_reclaim_apply_parameters()` constructs a temporary paddr context and scheme, validates attributes, sets the monitoring region, then commits to the live context.
- `damon_reclaim_turn()` starts/stops the exclusive DAMON context and installs a repeated `damon_call()` callback.
- Callback updates exported stats and applies committed parameter changes when `commit_inputs` is set.
- Initialization creates the paddr context and starts immediately if enabled by boot/module parameter.
