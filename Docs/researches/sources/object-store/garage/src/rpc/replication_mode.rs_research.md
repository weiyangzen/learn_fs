# sources/object-store/garage/src/rpc/replication_mode.rs

Purpose: parses and represents cluster replication factor and consistency mode configuration.

Important APIs and types: `ReplicationFactor(usize)` guarantees factor >= 1 through `new`; `ConsistencyMode` has `Dangerous`, `Degraded`, and default `Consistent`. Methods compute read and write quorums. `parse_replication_mode` converts `Config` fields into `(ReplicationFactor, ConsistencyMode)`.

Control flow: quorum behavior is mode-dependent. `Dangerous` reads and writes with quorum 1. `Degraded` reads with 1 but writes enough to satisfy the consistent write quorum. `Consistent` uses `ceil(replication_factor / 2)` read quorum and complementary write quorum. Parsing rejects the legacy `replication_mode`, requires `replication_factor`, validates factor and consistency string, and returns configuration errors.

State and persistence: values are serialized/deserialized and embedded in layout/history/status, but this file has no IO.

Dependencies and integration: used by layout creation/checks, table replication, system status validation, and config parsing. Implements `AutoCrdt` for `ConsistencyMode` with divergence warnings.

Risks and test signals: `Dangerous` can sacrifice consistency by design. Config mismatch between nodes is checked in `System::handle_advertise_status`; a higher remote replication factor forces process exit for safety. No direct tests here.
