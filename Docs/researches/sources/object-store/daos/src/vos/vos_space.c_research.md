# sources/object-store/daos/src/vos/vos_space.c

Purpose: implements VOS pool space accounting, reservation, admission control, and telemetry updates for SCM, NVMe, and evictable-pool non-evictable memory buckets. It is the local guard used before updates allocate persistent VOS metadata or data extents.

Important APIs/functions: `vos_space_sys_init` computes built-in system reservations from GC, aggregation, NVMe availability, tiny/small pool status, and `frag_reserve_space`. `vos_space_sys_set` recomputes defaults, adds caller-provided reservations, validates against pool totals, and rolls back on error. `vos_space_query` fills `vos_pool_space` with total/free/system fields and optional VEA stats. `vos_space_hold` estimates update or remove cost, verifies available capacity after system, held, and rebuild reservations, and increments held counters. `vos_space_unhold` releases held accounting. `vos_space_update_metrics` periodically publishes SCM/NVMe total and used gauges.

Control flow and state: reservations live in `vos_pool::vp_space_sys`, `vp_space_held`, and `vp_space_rb`; durable totals are read from `vp_pool_df`. Space queries call PMDK/umem heap usage for SCM and VEA for NVMe. `estimate_space` conservatively assumes new object/dkey/akey/tree nodes and accounts single-value records, array extents, checksums, and SCM-vs-NVMe placement via `vos_io_scm`.

Dependencies/integration: depends on `vos_internal.h`, umem/PMDK heap APIs, VEA allocator stats, checksum helpers, VOS record sizing helpers, DAOS telemetry, and rebuild/update flags such as `VOS_OF_CRIT`, `VOS_OF_REMOVE`, and `VOS_OF_REBUILD`.

Risks: estimates are intentionally coarse and can reject updates early or underrepresent unusual metadata growth. Critical and remove operations bypass checks. NVMe held space is treated differently because VEA free space already excludes reservations. PMDK heap usage can return invalid values, handled by clamping SCM free to zero. Metrics are rate-limited to one second and tolerate query errors by logging.

Test signals: exercise tiny/small pools, pools without NVMe, evictable pools, rebuild reserve percentages, `VOS_OF_REMOVE` and `VOS_OF_CRIT`, failed VEA/umem queries, hold/unhold counter balance assertions, and telemetry refresh throttling.
