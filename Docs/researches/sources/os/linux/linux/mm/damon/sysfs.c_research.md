# File Research: sources/os/linux/linux/mm/damon/sysfs.c

Implements the top-level DAMON sysfs administration interface under `/sys/kernel/mm/damon/admin`. It builds the kdamond/context/target/monitoring-attribute hierarchy, translates sysfs input into `damon_ctx` objects, starts and stops DAMON worker threads, commits live configuration, and dispatches update commands for scheme stats, tried regions, quotas, and tuned intervals.

Key responsibilities:
- Creates the root `damon/admin/kdamonds` sysfs tree during `subsys_initcall()`.
- Manages dynamic kdamond directories with `nr_kdamonds`, refusing to rebuild them while any represented kdamond is running.
- Restricts each kdamond to at most one context for now (`nr_contexts` must be `0` or `1`).
- Exposes context operations as `vaddr`, `fvaddr`, and `paddr`, with `avail_operations` filtered by registered DAMON ops.
- Exposes address unit, monitoring intervals, intervals feedback goal, min/max region count, targets, target regions, schemes, kdamond state, kdamond pid, and refresh interval.
- Converts configured targets and regions into runtime DAMON targets, including PID lookup for virtual-address operations.
- Dispatches user commands written to `state`.

Sysfs object model:
- `struct damon_sysfs_ui_dir` owns `kdamonds/`.
- `struct damon_sysfs_kdamonds` owns dynamic `kdamonds/<idx>/` entries and `nr_kdamonds`.
- `struct damon_sysfs_kdamond` owns `contexts/`, the active or last `damon_ctx`, and the periodic `refresh_ms` setting.
- `struct damon_sysfs_contexts` owns dynamic `contexts/<idx>/` entries, currently limited to one.
- `struct damon_sysfs_context` owns `monitoring_attrs/`, `targets/`, and `schemes/`.
- `struct damon_sysfs_targets` owns dynamic target entries; each target owns an `init_regions/regions` style child directory for explicit initial ranges.
- `struct damon_sysfs_attrs` owns `intervals/` and `nr_regions/`; `intervals/` owns `intervals_goal/`.

Command handling:
- `state` accepts `on`, `off`, `commit`, `commit_schemes_quota_goals`, `update_schemes_stats`, `update_schemes_tried_bytes`, `update_schemes_tried_regions`, `clear_schemes_tried_regions`, `update_schemes_effective_quotas`, and `update_tuned_intervals`.
- `on` builds a new `damon_ctx` from sysfs configuration, starts DAMON with `damon_start()`, stores the context, and installs a repeated DAMON callback for periodic sysfs refresh.
- `off` calls `damon_stop()` but keeps the context pointer until the next `on` or kdamond directory rebuild, preserving final monitoring results for users.
- `commit` builds a parameter context, first validates it against a test copy of the running context with `damon_commit_ctx()`, then commits it to the live context.
- Stats/effective quota/tuned interval updates run through `damon_call()` so the DAMON worker thread reads its own context safely.
- Tried-region updates use `damos_walk()` and the scheme helper file to repopulate `tried_regions/`.

Input validation:
- Negative counts for kdamonds, targets, regions, and similar directories are rejected; context count greater than one is rejected.
- `addr_unit` must be nonzero and is only meaningful for physical-address monitoring.
- Explicit region lists must be ordered and non-overlapping; `start > end` and overlap with the previous range are rejected.
- Physical-address monitoring rejects multiple targets because multiple physical address targets do not make sense.
- PID targets require `find_get_pid()` to succeed when the selected operations are PID-backed.
- DAMON attributes are validated by `damon_set_attrs()`, including interval and min/max region constraints.

Concurrency and lifecycle notes:
- `damon_sysfs_lock` serializes sysfs tree mutation and command execution.
- Dynamic directory stores use `mutex_trylock()` and return `-EBUSY` if the interface is busy.
- `state_store()` holds `damon_sysfs_lock` while parsing and dispatching commands.
- Runtime DAMON callbacks that update sysfs fields are scheduled through DAMON's call mechanism when they need to inspect internal context state.
- `damon_sysfs_repeat_call_fn()` periodically updates tuned intervals, scheme stats, and effective quotas when `refresh_ms` is nonzero.
- Kobject release for `damon_sysfs_kdamond` destroys any retained `damon_ctx`.

Relationships with other files:
- Uses `damon_sysfs_schemes_alloc()`, `damon_sysfs_add_schemes()`, `damos_sysfs_set_quota_scores()`, `damon_sysfs_schemes_update_stats()`, `damos_sysfs_update_effective_quotas()`, `damos_sysfs_populate_region_dir()`, and `damon_sysfs_schemes_clear_regions()` from `sysfs-schemes.c`.
- Includes `tests/sysfs-kunit.h` at the end so the static helpers can be tested when `CONFIG_DAMON_SYSFS_KUNIT_TEST` is enabled.
