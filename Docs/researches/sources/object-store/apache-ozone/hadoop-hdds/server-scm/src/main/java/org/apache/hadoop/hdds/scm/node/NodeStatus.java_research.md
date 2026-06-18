# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeStatus.java

Purpose: `NodeStatus` is an immutable value object combining datanode health (`NodeState`), operational state (`NodeOperationalState`), and optional operational-state expiry time used by maintenance mode.

Important APIs and types: Important APIs include `valueOf`, static sets `maintenanceStates`, `decommissionStates`, `outOfServiceStates`, status constants such as `inServiceHealthy`, `newNodeState`, `newOperationalState`, predicate methods such as `isNodeWritable`, `isDecommission`, `isMaintenance`, `isHealthy`, `isAlive`, `isDead`, `operationalStateExpired`, and value methods `equals`, `hashCode`, `toString`.

Control flow: `valueOf` returns cached singleton instances for expiry-zero combinations and creates a new object when expiry is non-zero. Predicate methods classify operational and health states using immutable enum sets. Expiry compares current wall-clock milliseconds to expiry epoch seconds.

State and persistence behavior: Instances are immutable and carry no external state. They model state that may be persisted by datanodes, but this class does not persist it. Singleton caching reduces allocations for common non-expiring states.

Dependencies and integration points: `NodeStateManager`, `NodeStateMap`, decommission/maintenance workflows, placement policies, and node-count APIs all use `NodeStatus` as the compact state filter and transition value.

Risks: `isAlive` returns true for `HEALTHY` and `STALE`, but not `HEALTHY_READONLY`, while `isHealthy` includes `HEALTHY_READONLY`; callers must choose carefully. `operationalStateExpired` uses wall-clock time, while heartbeat health uses monotonic time. Adding new enum values requires reviewing cached maps and predicate sets.

Test signals: Tests should cover cached identity for zero expiry, new instance for non-zero expiry, all predicate classifications, expiry boundary behavior, equality/hash including expiry, writable definition, and `toString` format.
