# File Research: sources/os/linux/linux/mm/damon/core.c

Core implementation of the DAMON framework: operation registration, context/target/region/scheme lifecycle, worker-thread management, adaptive region splitting/merging, DAMOS action scheduling, quota enforcement, and live parameter commits.

Key responsibilities:
- Registers/selects monitoring operation sets through `damon_register_ops()` and `damon_select_ops()`.
- Allocates and manages `damon_ctx`, `damon_target`, `damon_region`, `damos`, `damos_filter`, and `damos_quota_goal` objects.
- Provides `damon_set_regions()`, `damon_set_attrs()`, `damon_set_schemes()`, and `damon_commit_ctx()` for initial and live configuration.
- Starts/stops one `kdamond` thread per context through `damon_start()` and `damon_stop()`, with exclusive/non-exclusive group semantics.
- Supports in-thread callbacks via `damon_call()` and region-walk callbacks via `damos_walk()`.
- Applies DAMOS schemes with access-pattern matching, core/ops filters, watermarks, quotas, quota goals, and action statistics.
- Dynamically adapts monitored regions by merging similar adjacent regions and splitting regions when region count falls low.
- Auto-tunes monitoring intervals using an access-rate feedback loop when `intervals_goal` is configured.

Important flows:
- `kdamond_fn()` initializes context state, waits for watermark activation, prepares access checks, sleeps for the sample interval, checks accesses, merges/splits regions, handles calls, applies schemes, resets aggregation, and invokes ops updates.
- `damos_apply_scheme()` bounds application by quota, splits oversized regions if needed, applies core filters, calls the backend `apply_scheme`, records charged time/size, updates stats, and resets region age for non-stat actions.
- `damos_adjust_quota()` computes effective quota from size/time caps and feedback goals, then uses backend scores to set `quota->min_score`.
- `damon_commit_ctx()` updates schemes, targets, attributes, ops, address unit, and minimum region size while marking the destination context as temporarily possibly corrupted so kdamond can stop on unsafe updates.
- `damon_set_region_biggest_system_ram_default()` finds the largest System RAM resource when a physical-monitoring module does not specify an explicit range.

Concurrency and lifecycle notes:
- Global `damon_lock` tracks running contexts and exclusive runs.
- Per-context locks protect kdamond pointer, call-control list, and walk-control state.
- `kdamond_call()` cancels pending callbacks on shutdown and can stop processing when a callback corrupts context state.
- `kdamond_fn()` destroys targets on exit, cancels pending calls/walks, clears `ctx->kdamond`, and decrements global running count.
