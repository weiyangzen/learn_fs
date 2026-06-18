# File Research: sources/os/linux/linux/mm/damon/sysfs-schemes.c

Implements the DAMON sysfs subtree for DAMOS schemes. It defines the per-scheme kobject hierarchy below a context's `schemes` directory, exposes all tunable scheme parameters, converts sysfs configuration into runtime `struct damos` objects, and mirrors runtime statistics/tried-region snapshots back into sysfs.

Key responsibilities:
- Creates and destroys `schemes/<idx>/` kobjects and nested directories for `access_pattern`, `dests`, `quotas`, `watermarks`, `filters`, `core_filters`, `ops_filters`, `stats`, and `tried_regions`.
- Exposes DAMOS action names (`willneed`, `cold`, `pageout`, `hugepage`, `nohugepage`, `lru_prio`, `lru_deprio`, `migrate_hot`, `migrate_cold`, `stat`) through the `action` attribute.
- Represents access-pattern bounds using shared `damon_sysfs_ul_range` directories for size, access count, and age.
- Manages quotas, quota weights, quota goals, effective quota reporting, and quota goal tuner mode.
- Represents watermark controls with metric, interval, high, mid, and low attributes.
- Represents migration destinations as dynamically sized `dests/<idx>/` entries with node id and weight.
- Represents filters split into legacy/all (`filters`), core-handled (`core_filters`), and ops-handled (`ops_filters`) directories.
- Converts configured filters, quota goals, migration destinations, and action parameters into `struct damos` instances used by the DAMON core.
- Updates sysfs-visible scheme stats and tried-region snapshots from running DAMON contexts.

Sysfs object model:
- `struct damon_sysfs_schemes` owns a dynamic array of `struct damon_sysfs_scheme *` and the `nr_schemes` attribute.
- `struct damon_sysfs_scheme` owns the complete per-scheme subtree and stores action, apply interval, and target NUMA node.
- `struct damon_sysfs_stats` exposes `nr_tried`, `sz_tried`, `nr_applied`, `sz_applied`, `sz_ops_filter_passed`, `qt_exceeds`, `nr_snapshots`, and writable `max_nr_snapshots`.
- `struct damon_sysfs_scheme_regions` owns the tried-region list and `total_bytes`; each `struct damon_sysfs_scheme_region` exposes start, end, access count, age, and filter-passed bytes.
- `struct damon_sysfs_scheme_filter` stores filter type, matching polarity, allow/reject behavior, memcg path, address range, hugepage-size range, and target index.

Important flows:
- `nr_schemes_store()` parses the requested scheme count, takes `damon_sysfs_lock`, and calls `damon_sysfs_schemes_add_dirs()` to rebuild the scheme directory array.
- `damon_sysfs_scheme_add_dirs()` creates all mandatory nested directories for a scheme and carefully unwinds partially created kobjects on error.
- `damon_sysfs_mk_scheme()` builds a runtime `struct damos` from one sysfs scheme by copying access pattern, action, apply interval, quotas, watermarks, target node, quota goals, filters, migration destinations, and max snapshot count.
- `damon_sysfs_add_schemes()` iterates configured sysfs schemes, creates runtime DAMOS schemes, and adds them to a `damon_ctx`; on failure it destroys any schemes already added to the context.
- `damos_sysfs_set_quota_scores()` commits only quota goals into an already running DAMON context, allowing live quota feedback updates without rebuilding the full context.
- `damon_sysfs_schemes_update_stats()` copies runtime scheme counters into `stats/`.
- `damos_sysfs_populate_region_dir()` is called during a DAMOS walk to populate `tried_regions/` or only accumulate `total_bytes`.
- `damon_sysfs_schemes_clear_regions()` removes all tried-region child kobjects and resets total bytes.

Validation and conversion details:
- Filter type strings are validated against the filter directory's handling layer: `core_filters` rejects ops-only filters, `ops_filters` accepts only ops-handled filters, and `filters` accepts both.
- Memcg filters and memcg quota goals resolve a user-provided cgroup path into a memcg id using `mem_cgroup_iter()` and skip offline memcgs.
- Address filters reject `end < start`; hugepage-size filters reject `min > max`.
- Quota goals with `target_value == 0` are skipped during runtime conversion.
- Node/memcg quota goals copy `nid` and resolve memcg ids as needed; user-input quota goals copy the current value directly.
- Migration destinations allocate node-id and weight arrays on the runtime scheme; if no destinations are configured, the vaddr backend falls back to the scheme's `target_nid`.

Concurrency and lifecycle notes:
- Dynamic directory count stores use `mutex_trylock(&damon_sysfs_lock)` and return `-EBUSY` if sysfs state is being used by command handling.
- String attributes such as filter `memcg_path` and quota goal `path` allocate a replacement buffer before taking the lock, then swap and free the previous value while locked.
- Kobject release functions own final `kfree()` of their containing sysfs structs; array rebuild functions drop references with `kobject_put()`.
- The code assumes parent removal routines remove child directories before dropping the parent kobject.

Notable detail:
- `damos_sysfs_populate_region_dir()` increments `sysfs_regions->nr_regions` both in the child name argument and again after `list_add_tail()`, which means the counter advances by two for a successfully materialized tried-region entry. That behavior is worth checking against expected sysfs naming/count semantics if this area is modified.
