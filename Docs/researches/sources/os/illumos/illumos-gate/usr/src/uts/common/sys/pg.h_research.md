# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pg.h

## Purpose
Defines the kernel processor-group framework for grouping CPUs by logical or physical relationships and dispatching CPU/thread events to group classes.

## Main Interfaces
- Types:
  - `pgid_t`
  - `pg_cid_t`
  - `pg_relation_t`
  - `pg_cb_ops_t`
  - `pg_t`
  - `struct pg_ops`
  - `pg_class_t`
  - `cpu_pg_t`
  - `pg_cpu_itr_t`
- CPU iteration helpers:
  - `PG_CPU_ITR_INIT`
  - `PG_CPU_GET_FIRST`
  - `PG_NUM_CPUS`
- Framework routines:
  - `pg_init()`
  - `pg_class_register()`
- CPU lifecycle hooks:
  - `pg_cpu0_init()`
  - `pg_cpu_init()`
  - `pg_cpu_fini()`
  - `pg_cpu_active()`
  - `pg_cpu_inactive()`
  - `pg_cpu_startup()`
  - `pg_cpu_bootstrap()`
- CPU partition and group manipulation:
  - `pg_cpupart_in()`
  - `pg_cpupart_out()`
  - `pg_cpupart_move()`
  - `pg_create()`
  - `pg_destroy()`
  - `pg_cpu_add()`
  - `pg_cpu_delete()`
  - `pg_cpu_find_pg()`
  - `pg_cpu_next()`
  - `pg_cpu_find()`
- Event/observability:
  - `pg_callback_set_defaults()`
  - `pg_ev_thread_swtch()`
  - `pg_ev_thread_remain()`
  - `pg_policy_name()`

## Dependencies And Relationships
Visible for `_KERNEL` and `_KMEMUSER`. Includes CPU, group, processor, bitset, atomic, types, and kstat headers. Physical processor groups are extended by `pghw.h`.

## Research Notes
The framework separates processor group class registration from concrete CPU membership. Callback vectors let scheduling and observability code react to thread switch/remain events.
