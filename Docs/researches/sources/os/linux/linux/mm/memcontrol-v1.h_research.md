# File Research: sources/os/linux/linux/mm/memcontrol-v1.h

## Purpose

Declares the interface between generic memory cgroup code and the cgroup v1-specific implementation in `memcontrol-v1.c`. It also provides no-op stubs when `CONFIG_MEMCG_V1` is disabled, allowing shared memcg code to compile without scattering configuration checks.

## Common Declarations

The header defines iteration helpers used by both cgroup v1 and v2 paths:

- `for_each_mem_cgroup_tree(iter, root)`
- `for_each_mem_cgroup(iter)`

Both use `mem_cgroup_iter()` and require callers to use `mem_cgroup_iter_break()` if they exit early.

Common declarations include:

- `drain_all_stock()`
- `memcg_events()`
- `memory_stat_show()`
- `mem_cgroup_private_id_get_online()`

These are shared with the broader memcg implementation.

## CONFIG_MEMCG_V1 Interface

When cgroup v1 memory controller support is enabled, the header declares:

- `do_memsw_account()`: true on legacy hierarchy, false on cgroup v2 default hierarchy.
- event counter helpers: `memcg_events_local()`, `memcg_page_state_local()`, `memcg_page_state_local_output()`.
- allocation lifecycle: `memcg1_alloc_events()`, `memcg1_free_events()`, `memcg1_memcg_init()`.
- tree and lifecycle hooks: `memcg1_remove_from_trees()`, `memcg1_css_offline()`.
- soft-limit reset: `memcg1_soft_limit_reset()`.
- OOM hooks: `memcg1_oom_prepare()`, `memcg1_oom_finish()`, `memcg1_oom_recover()`.
- charge hooks: `memcg1_commit_charge()`, `memcg1_uncharge_batch()`.
- stats hooks: `memcg1_stat_format()`, `reparent_memcg1_state_local()`, `reparent_memcg1_lruvec_state_local()`.
- generic stat reparent helpers implemented elsewhere: `reparent_memcg_state_local()`, `reparent_memcg_lruvec_state_local()`.
- kmem and socket memory hooks: `memcg1_account_kmem()`, `memcg1_tcpmem_active()`, `memcg1_charge_skmem()`, `memcg1_uncharge_skmem()`.
- legacy cftype arrays: `memsw_files[]`, `mem_cgroup_legacy_files[]`.

It also defines `enum res_type` for encoding legacy control-file resource classes:

- `_MEM`
- `_MEMSWAP`
- `_KMEM`
- `_TCP`

## Disabled CONFIG_MEMCG_V1 Behavior

When `CONFIG_MEMCG_V1` is disabled, the header provides inline stubs:

- memsw accounting is always false;
- event allocation succeeds trivially;
- init, cleanup, soft-limit, OOM, charge, uncharge, stat, and kmem hooks become no-ops;
- socket memory charging always succeeds;
- TCP memory accounting is reported inactive.

This keeps callers simple while removing legacy behavior from builds that do not support it.

## Integration Notes

The header is included by shared memcg code and by `memcontrol-v1.c`. Its main role is to isolate legacy cgroup v1 behavior behind a compact API boundary.

The inline stubs are important because the rest of the memory controller can call `memcg1_*` hooks unconditionally without paying for cgroup v1 implementation when it is disabled.
