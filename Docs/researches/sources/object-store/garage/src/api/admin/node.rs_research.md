# sources/object-store/garage/src/api/admin/node.rs

Purpose: implements local node information, metadata snapshot, and node statistics endpoints.

Important handlers/functions: `LocalGetNodeInfoRequest` returns local node ID, hostname, version/build info, DB engine, address, role, draining state, and disk partitions. `LocalCreateMetadataSnapshotRequest` triggers asynchronous metadata snapshot creation. `LocalGetNodeStatisticsRequest` builds compatibility free-form text plus structured table and block-manager statistics. `gather_table_stats` reads per-table approximate item counts, Merkle tree size, Merkle queue, insert queue, and GC queue.

Control flow and state: reads local system status, current/old layout versions, known nodes, database engine metadata, many Garage metadata tables, and block manager queues. Snapshot endpoint delegates to `garage_model::snapshot::async_snapshot_metadata`, which persists snapshot artifacts outside this file.

Dependencies/integration: depends on Garage system/local status, layout history, version helpers, DB engine, table replication/schema traits, block manager stats, optional `k2v` feature tables, `format_table`, and local admin RPC wrappers.

Risks: statistics are approximate and some fields are retained as free-form compatibility text. `garage_features().unwrap()` in statistics assumes build feature metadata exists. Draining detection compares current role absence with older layout presence. Adding new metadata tables requires updating statistics coverage.

Test signals: cover node info for storage/gateway/draining states, disk info presence/absence, snapshot success/failure propagation, table stats for all included tables, k2v feature builds, block manager queue counts, and behavior when feature metadata is unavailable.
