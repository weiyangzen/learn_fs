# sources/object-store/daos/src/pool/srv_pool_map.c

## Purpose
`srv_pool_map.c` applies target-state operations to an in-memory DAOS pool map and advances the map version only when actual target or rank-domain state changes occur. It is the shared state-transition engine behind exclude, drain, reintegrate, extend, rebuild finish, and rebuild revert paths.

## Important APIs, types, and functions
The exported function is `ds_pool_map_tgts_update(uuid_t pool_uuid, struct pool_map *map, struct pool_target_id_list *tgts, int opc, bool exclude_rank, uint32_t *tgt_map_ver, bool print_changes)`. Internal helpers are `update_one_tgt`, `update_one_dom`, `update_tgt_up_to_upin`, and `update_tgt_down_drain_to_downout`. It manipulates `struct pool_target`, `struct pool_domain`, `struct pool_target_id_list`, component status fields, component flags, in/out versions, failure sequence (`co_fseq`), and pool-map version.

## Control flow
`ds_pool_map_tgts_update` starts from the current pool-map version, iterates each requested target ID, resolves the `pool_target` and owning rank domain, applies `update_one_tgt`, then optionally updates the rank-domain state through `update_one_dom`. At the end it sets `*tgt_map_ver` to the highest target-related version or zero if no target changed, and updates the map's version only if the local version advanced.

`update_one_tgt` encodes the legal status machine. `MAP_EXCLUDE` moves UP/UPIN to DOWN and refuses NEW. `MAP_DRAIN` allows only UPIN to DRAIN and refuses NEW/UP. `MAP_REINT` moves DOWN/DOWNOUT to UP and records DOWN2UP when appropriate. `MAP_EXTEND` promotes NEW to UP. `MAP_ADD_IN` promotes UP to UPIN. `MAP_EXCLUDE_OUT` and `MAP_FINISH_REBUILD` finalize DOWN/DRAIN to DOWNOUT and UP to UPIN. `MAP_REVERT_REBUILD` reverses DRAIN or UP transitions back to their prior states using flags and fseq.

## State and persistence behavior
This file mutates an in-memory pool-map object; persistence happens later through the pool service that stores and broadcasts the map. Versioning is precise: `co_in_ver`, `co_out_ver`, and `co_fseq` record when targets entered or left active service, while the pool map's global version is only bumped after at least one real state change. Domain updates keep rank-level status consistent with target transitions, especially SWIM rank eviction and rebuild completion.

## Dependencies and integration points
Callers include pool-service map update logic in `srv_pool.c`, with declaration in `srv_pool_map.h`. The code depends on DAOS pool-map helpers such as `pool_map_find_target`, `pool_map_find_dom_by_rank`, `pool_map_node_status_match`, `update_dom_status_by_tgt_id`, and `pool_map_set_version`. It integrates with rebuild, reintegration, extension, drain, and SWIM exclusion workflows.

## Risks and test signals
The major risks are illegal state transitions, version increments on no-ops, rank-domain status drifting from target status, and incorrect rebuild revert behavior when `PO_COMPF_DOWN2UP` or `co_fseq` is involved. Tests should cover every operation/status pair, repeated idempotent requests, mixed target batches, nonexistent targets/ranks, `exclude_rank` domain updates, and `tgt_map_ver == 0` when no rebuild/reintegration ULT should be scheduled.
