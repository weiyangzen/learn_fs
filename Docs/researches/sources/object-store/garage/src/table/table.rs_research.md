<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/table.rs -->
# sources/object-store/garage/src/table/table.rs

## Purpose
Generic distributed table facade for Garage metadata tables. `Table<F, R>` binds a schema, a replication policy, local table storage, Merkle maintenance, anti-entropy sync, garbage collection, insert queueing, and an RPC endpoint into the API used by higher-level model code.

## Important APIs, types, and functions
Key types are `Table<F, R>` and private `TableRpc<F>`. Public calls are `new`, `spawn_workers`, `insert`, `queue_insert`, `insert_many`, `get`, `get_range`, and `get_local`; internal helpers include `insert_internal`, `insert_many_internal`, `get_internal`, `get_range_internal`, and `repair_on_read`. The endpoint handler serves `ReadEntry`, `ReadRange`, and `Update` RPCs.

## Control flow
Construction creates `TableData`, `MerkleUpdater`, `TableSyncer`, `TableGc`, registers the table name in the layout manager, and installs itself as the Netapp endpoint handler. Writes compute partition hashes, ask replication for write sets, encode entries, then send update RPCs to enough nodes for write quorum. Batched writes deduplicate write sets, build per-node payloads, and track quorum with `QuorumSetResultTracker`. Reads query read nodes, merge divergent CRDT entries, and spawn repair-on-read updates when responses disagree.

## State and persistence behavior
Local persistence lives behind `TableData` and the underlying Garage DB transaction/tree APIs; this file coordinates when serialized entries are written locally or sent remotely. Merkle updater, syncer, GC, and insert queue workers maintain convergence and cleanup outside the request path. Read repair is asynchronous and best-effort after a successful client read.

## Dependencies and integration points
Integrates `garage_rpc` endpoints, `System`, `RequestStrategy`, OpenTelemetry tracing, table schema/replication traits, CRDT merging, table data encoding, Merkle/sync/GC workers, and Garage utility metrics/errors. Higher-level bucket/object/key tables rely on these generic semantics.

## Risks and test signals
Quorum accounting is the critical risk: wrong write-set deduplication, stale layout locks, or premature success can break read-after-write guarantees. Range reads must trim to the requested limit after merging node responses so later entries without read quorum are not returned. Useful tests are distributed write/read quorum failures, divergent replicas triggering repair, range limit/order behavior, and endpoint rejection of unexpected RPC variants.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/table.rs -->
