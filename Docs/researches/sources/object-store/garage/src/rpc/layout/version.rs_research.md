# sources/object-store/garage/src/rpc/layout/version.rs

Purpose: implements the active layout version behavior: node/partition accessors, consistency checks, next-version computation, capacity-optimal assignment, rebalance minimization, and computation reporting.

Important APIs and types: `LayoutVersion::new`, `all_nodes`, `nongateway_nodes`, `node_role`, `partition_of`, `partitions`, `nodes_of`, quorum helpers, `check`, `calculate_next_version`, `calculate_partition_assignment`, `generate_nongateway_zone_ids`, and `ComputationStat` with zone/node stat structs.

Control flow: `calculate_next_version` merges staged roles, prunes removed roles, applies parameters, and calls `calculate_partition_assignment`. Assignment updates node IDs, determines effective zone redundancy, validates enough storage nodes/zones, computes maximal feasible partition size by binary search with max flow, computes a candidate assignment biased toward previous edges, optimizes rebalance with negative-cycle cost improvements, emits stats, writes `ring_assignment_data`, and rechecks invariants. `check` validates assignment length, node sets, no gateway assignments, distinct replicas per partition, zone redundancy, capacity limits, and optimal partition size.

State and persistence: `LayoutVersion` is part of persisted `LayoutHistory`. `ring_assignment_data` stores compact node indices for each partition replica; `partition_size` is persisted for checks and reporting.

Dependencies and integration: uses graph algorithms, CRDT maps, `bytesize`, `itertools`, `utoipa`, and replication-mode quorum logic. Table sharded replication relies on `nodes_of` and partition iteration.

Risks and test signals: this file carries the highest algorithmic risk. Capacity math uses integer division and requires viable capacities; small partition sizes trigger warnings. Any change to `PARTITION_BITS`, compact node type, or assignment ordering affects data placement. `layout/test.rs` exercises several reassignment scenarios but not all edge cases.
