# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_network.rs

## Purpose
Defines internode network metric descriptors for failed calls, dial failures, average dial time, and bytes sent/received between peers.

## Important APIs, Types, and Functions
Exports five descriptors under `subsystems::SYSTEM_NETWORK_INTERNODE`. Error and byte totals are counters; average dial time is a gauge. All are unlabeled.

## Control Flow
Lazy descriptor initialization only.

## State and Persistence
No values. `collect_internode_network_stats()` reads `global_internode_metrics().snapshot()`.

## Dependencies and Integration Points
Used by `metrics/collectors/system_network.rs`. The stats collector wraps internode metrics into `NetworkStats`.

## Risks
Unlabeled aggregate metrics do not identify peer nodes or endpoints. Counters are process-lifetime values from the global runtime. Average dial time semantics depend on the internode metrics implementation.

## Test Signals
No schema-local tests. Collector tests should verify names and counter/gauge typing.
