# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pghw.h

## Purpose
Defines hardware-backed processor groups that represent shared CPU resources such as caches, memory pipes, chips, memory domains, and power-management domains.

## Main Interfaces
- `pghw_type_t`: hardware sharing types including instruction pipeline, cache, FPU, memory pipe, chip, memory, active power domain, and idle power domain.
- `PGHW_PROCNODE`: aliases processor nodes to memory-pipe-style sharing.
- `PGHW_IS_PM_DOMAIN(hw)`: tests power-management domain types.
- `PGHW_INSTANCE_ANON`: anonymous instance sentinel.
- `pghw_handle_t`: platform-specific opaque handle.
- `pghw_util_t`: capacity/utilization counters and timestamps.
- `pghw_t`: embeds `pg_t` and adds hardware type, instance, kstats, generation, CPU list, and utilization state.
- `cpu_physid_t`: chip/core/cache identifiers for a CPU.
- Lifecycle and lookup routines:
  - `pghw_init()`, `pghw_fini()`, `pghw_cpu_add()`, `pghw_place_cpu()`, `pghw_cmt_fini()`
  - `pghw_physid_create()`, `pghw_physid_destroy()`
  - `pghw_find_pg()`, `pghw_find_by_instance()`, `pghw_set_lookup()`
- Platform hooks:
  - `pg_plat_hw_shared()`
  - `pg_plat_cpus_share()`
  - `pg_plat_hw_instance_id()`
  - `pg_plat_hw_rank()`
  - `pg_plat_get_core_id()`
- `pghw_type_string()`: string representation for hardware type.

## Dependencies And Relationships
Extends `pg.h` and includes CPU, group, processor, bitmap, atomic, types, and kstat support. Platform-specific CPU topology code supplies the sharing and ranking hooks.

## Research Notes
The header explicitly avoids a `PGHW_CORE` type because “core” varies by platform. Capacity/utilization kstats depend on generation tracking and a cached CPU list.
