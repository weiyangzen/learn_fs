# sources/object-store/daos/src/pool/srv_util.c

## Purpose
`srv_util.c` provides shared pool-server utility logic: rank and target list construction from pool maps, collective/broadcast helpers, pool-map bulk transfer, pool-service replica reconfiguration planning, target-state lookup, failed-target discovery, and NVMe faulty/reintegration reactions.

## Important APIs, types, and functions
Public APIs include `map_ranks_init`, `map_ranks_failed`, `map_ranks_fini`, `ds_pool_map_rank_up`, `ds_pool_bcast_create`, `ds_pool_transfer_map_buf`, `ds_pool_plan_svc_reconfs`, `ds_pool_get_ranks`, `ds_pool_get_tgt_idx_by_state`, `ds_pool_get_failed_tgt_idx`, `ds_pool_thread_collective[_reduce]`, `ds_pool_task_collective[_reduce]`, and the exported `nvme_reaction_ops`. Internal planning types are `struct reconf_domain` and `struct reconf_map`; NVMe reaction state uses `struct update_targets_arg`.

## Control flow
Rank helpers scan the pool map's rank domains and produce `d_rank_list_t` values matching requested component states. `ds_pool_bcast_create` builds an excluded-rank list from DOWN/DOWNOUT ranks plus optional caller exclusions, then creates a CORPC request over the pool group. `ds_pool_transfer_map_buf` validates remote bulk size, then performs a bulk PUT of a cached pool-map buffer and reports `-DER_TRUNC` with the required size when needed.

Pool-service reconfiguration planning starts with `compute_svc_reconf_objective`, initializes an ephemeral map of desired domains and existing replicas through `init_reconf_map`, removes undesired/out-of-map replicas, adds replacements with randomized but balanced domain selection, removes excess replicas from crowded domains, and finally calls `balance_replicas` to improve distribution. `filter_only` short-circuits after identifying undesired replicas.

Collective helpers build a bitmap of excluded local target indexes based on pool-map target states and dispatch thread or task collectives. NVMe reactions are intentionally asynchronous relative to hardware polling. `nvme_reaction` lists SMD pools, optionally starts affected pool children for reintegration, checks whether affected targets are already in the expected pool-map state, submits client-side exclude/reintegrate requests to the pool leader when needed, and tears down targets after successful faulty exclusion. System target failure kills the engine; system target auto-reintegration is rejected.

## State and persistence behavior
Most functions read volatile cached pool maps and return heap-allocated rank/target lists to callers. Broadcast and map bulk helpers operate over CRT/IV state without modifying persistence. Service reconfiguration planning is pure except for random placement decisions. NVMe reaction paths change persistent/cluster-visible state indirectly through pool service target exclude/reintegrate RPCs and local pool-child start/stop, reflecting SMD device replacement or failure state.

## Dependencies and integration points
The file depends on pool-map traversal APIs, CRT CORPC/bulk APIs, Argobots event synchronization, SMD pool lists, BIO reaction hooks, DAOS client pool target update calls, and target-child lifecycle APIs from `srv_target.c`. `srv_pool_scrub_ult.c` uses `ds_pool_get_ranks` for drain destinations; `srv_target.c` uses collective helpers and target-index filtering; pool service code uses reconfiguration planning for service replica membership.

## Risks and test signals
Risks include rank-list leaks, empty-map handling, excluding the wrong local targets from collectives, reconfiguration imbalance or attempts to remove the current leader from an undesired state, nondeterminism from randomized placement, and NVMe reaction loops that repeatedly send exclude/reint while pool maps are stale. The disabled in-file unit tests define many service-reconfiguration edge cases. Additional tests should cover down ranks, all-targets-down rank failure classification, bulk truncation, collective target bitmaps, SMD/pool-map inconsistency tolerance, system target failure policy, and reint/faulty transitions returning 0/1/error according to `bio_reaction_ops`.
