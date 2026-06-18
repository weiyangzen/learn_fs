# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pghw.c

## Purpose

`pghw.c` implements the hardware-sharing layer for processor groups. It extends generic `pg_t` objects into `pghw_t` objects that represent shared hardware resources such as sockets, caches, integer pipelines, FPUs, memory links, and CPU power domains.

Read completely: 749 lines.

## Main Responsibilities

- Organizes hardware PGs into per-hardware-type sets.
- Initializes and finalizes `pghw_t` metadata and power-management handles.
- Finds hardware PGs by CPU, hardware type, or platform instance ID.
- Manages per-CPU physical ID cache memory.
- Exports processor group topology and capacity/utilization data through kstats.
- Maintains CPU-list strings and generation counters for kstat snapshots.

## Hardware Set Model

`pg_hw` is a top-level `group_t` indexed by `pghw_type_t`. Each slot points to a hardware set containing all `pghw_t` instances of that sharing type.

`pghw_set_create()` creates `pg_hw` on first use, expands it to `PGHW_NUM_COMPONENTS`, creates a new type-specific group, and inserts it at the hardware type index.

`pghw_set_lookup()` returns the group for a hardware type, while `pghw_set_add()` and `pghw_set_remove()` maintain PG membership in that set.

## PG Initialization and Lookup

`pghw_init()` creates the hardware set if needed, adds the PG to it, records the hardware type, generation, and platform instance ID from `pg_plat_hw_instance_id()`, creates kstats, and initializes CPU power-management domains for active or idle power PGs.

`pghw_fini()` tears down CMT-specific PG state, removes the PG from its hardware set, invalidates instance and hardware type fields, and deletes the generic hardware kstat.

`pghw_cmt_fini()` frees the cached CPU-list string and deletes the capacity/utilization kstat.

Lookup helpers include `pghw_place_cpu()`, `pghw_find_pg()`, and `pghw_find_by_instance()`.

## Physical ID Cache

`pghw_physid_create()` allocates `cpu_physid_t` for a CPU and initializes every ID field to the CPU ID. Platform code can later overwrite relationship-specific IDs.

`pghw_physid_destroy()` frees the cache.

## Kstats

`pghw_kstat_create()` creates two virtual kstats:

- `pg:<pg_id>:pg`, exposing PG ID, class, CPU count, instance ID, hardware relationship string, and policy string.
- `pg_hw_perf:<pg_id>:<relationship>`, exposing parent PG ID, CPU list, generation, hardware relationship, utilization counters, running/stopped time, current rate, and maximum rate.

`pghw_kstat_update()` fills the basic topology fields and rejects writes with `EACCES`.

`pghw_cu_kstat_update()` checks `secpolicy_cpc_cpu()` before exposing utilization data, updates CPU-list strings and hardware utilization under a nonblocking `mutex_tryenter(&cpu_lock)`, and zeroes utilization data for callers lacking CPC privilege.

`pghw_cpulist_alloc()` allocates or invalidates the cached CPU-list string based on CPU count and `pghw_generation`.

`pghw_parent_id()` returns the parent CMT PG ID when the PG belongs to the `cmt` class, otherwise -1.

## Hardware Type Names

`pghw_type_string()` maps hardware types to user-readable names such as `Integer Pipeline`, `Cache`, `Floating Point Unit`, `Socket`, `Memory`, and CPU power-domain names.

## Notable Invariants

- `pghw_t` embeds `pg_t` as its first field so generic PG pointers can be cast safely.
- Hardware sets are created dynamically but not destroyed.
- CU kstat update must not block on `cpu_lock` because kstat deletion can occur while `cpu_lock` is held.
- Hardware utilization visibility is privilege-gated by `PRIV_CPC_CPU`.

## Research Relevance

This file provides CPU topology observability that can explain filesystem and storage benchmark behavior on NUMA or CMT systems. It is also an example of privilege-gated kernel kstats.
