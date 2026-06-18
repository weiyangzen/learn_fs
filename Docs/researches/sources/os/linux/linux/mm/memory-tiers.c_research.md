# File Research: sources/os/linux/linux/mm/memory-tiers.c

## Role

Linux memory-tiering infrastructure. It groups NUMA memory nodes into ordered tiers by abstract memory distance, publishes memory-tier devices in sysfs, assigns each node a memory type, computes demotion targets for reclaim/migration, and supports performance-based tier distance algorithms.

## Key Behavior

- Defines `struct memory_tier` as an ordered tier with memory types, an abstract-distance chunk, a sysfs device, and a mask of all lower-tier nodes.
- Defines per-node `node_memory_type_map` entries with a memory device type and map count so multiple devices on one node can share one type reference.
- Registers the virtual `memory_tiering` bus and exposes each tier’s `nodelist` attribute.
- Groups memory types into tiers by rounding `memtype->adistance` down to `MEMTIER_CHUNK_SIZE`, keeping `memory_tiers` sorted by increasing abstract distance.
- Assigns nodes to tiers in `set_node_memory_tier()` using registered abstract-distance algorithms, or a default DRAM memory type when no specific type exists.
- Updates `NODE_DATA(node)->memtier` with RCU and uses `synchronize_rcu()` before unlinking node/type/tier relationships.
- Exports memory type helpers: `alloc_memory_type()`, `put_memory_type()`, `init_node_memory_type()`, `clear_node_memory_type()`, `mt_find_alloc_memory_type()`, and `mt_put_memory_types()`.
- Under NUMA migration, computes demotion chains by finding the closest nodes in the next lower tier and stores preferred demotion nodes per source node.
- Builds each tier’s `lower_tier_mask` so allocation fallback can target any lower-tier memory if preferred demotion nodes are unavailable.
- Determines top-tier status by locating the highest tier containing CPU nodes; promotion is avoided from tiers that include compute.
- `next_demotion_node()` filters preferred demotion targets by an allowed mask, randomly selects among equally preferred nodes, and falls back to `find_next_best_node()`.
- Under NUMA balancing, `folio_use_access_time()` repurposes `_last_cpupid` as access-time storage for non-top-tier folios when memory-tiering balancing mode is enabled.
- Provides default DRAM performance reference handling through `mt_set_default_dram_perf()` and converts performance coordinates to abstract distance with `mt_perf_to_adistance()`.
- Rejects the default DRAM performance algorithm if DRAM node latency or bandwidth differs from the reference by more than the built-in tolerance.
- Uses a blocking notifier chain for external abstract-distance algorithms via `register_mt_adistance_algorithm()`, `unregister_mt_adistance_algorithm()`, and `mt_calc_adistance()`.
- Handles memory hotplug: first memory on a node assigns a tier and recomputes demotion targets; last memory removal clears the tier and recomputes targets.
- Adds `/sys/kernel/mm/numa/demotion_enabled` when configured, and clears kswapd hopeless-state accounting when demotion is enabled.

## Dependencies

Uses NUMA node masks and node states, `pg_data_t->memtier`, RCU, krefs, sysfs devices and kobjects, memory hotplug notifiers, blocking notifier chains, scheduler NUMA balancing mode, migration/demotion policy, and kswapd reclaim state.

## Research Notes

This file owns the policy data model for heterogeneous memory placement. Device drivers can provide memory types or distance algorithms, while the core keeps tier membership, demotion masks, hotplug updates, and user-visible toggles coherent under `memory_tier_lock` plus RCU-protected readers.
