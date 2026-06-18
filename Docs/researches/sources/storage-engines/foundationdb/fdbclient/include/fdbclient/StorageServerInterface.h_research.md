<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerInterface.h

## Purpose
`StorageServerInterface.h` defines the durable RPC interface and request/reply payloads used by clients, proxies, ratekeeper, data distribution, audit, checkpoint, change feed, and bulk dump code to communicate with a storage server. It also defines storage metrics types and small helpers used by read routing and MVCC storage sizing.

## Important APIs, Types, and Functions
Important exports include `StorageServerInterface`, `StorageInfo`, `StorageServerMetaInfo`, `ServerCacheInfo`, `GetValueRequest/Reply`, `GetKeyRequest/Reply`, range read and mapped-range read request/reply types, streaming range replies, `WatchValueRequest/Reply`, `GetShardStateRequest/Reply`, `StorageMetrics`, `WaitMetricsRequest`, `SplitMetricsRequest/Reply`, `ReadHotRangeWithMetrics`, checkpoint fetch requests, obsolete change feed request types, queuing metrics, hot shard and checksum requests, `BulkDumpRequest`, and `mvccStorageBytes`.

## Control Flow
The interface object carries endpoint streams for every storage-server RPC. Callers serialize a request containing keys, version, tags, read options, span context, version-vector freshness information, and a reply promise. The storage server actor consumes the matching endpoint, validates shard ownership, reads local state, and replies with either load-balanced data, metrics, or streamed chunks. Metrics requests are used by data distribution to wait for thresholds, split ranges, and discover read-hot subranges. Checkpoint and bulk dump requests initiate server-side checkpoint lookup or data transfer.

## State and Persistence Behavior
`StorageServerInterface` is persisted in the database under server-list system keys, so its serialization is guarded by protocol-version assertions and reinitializes derived endpoints from `getValue` on deserialization. Several obsolete change-feed types remain because request-stream members of the persisted interface still depend on their type identifiers. Request objects hold transient arenas and reply promises; metric and checksum replies serialize operational state but do not persist it by themselves. `mvccStorageBytes` estimates in-memory mutation cost using `VersionedMap` overhead.

## Dependencies and Integration Points
This header depends on FoundationDB RPC primitives, load balancing, locality, tracing, queue metrics, `CommitTransaction`, `TagThrottle`, `VersionVector`, `StorageCheckpoint`, audit and bulk dump metadata, and storage-server shard state. It is integrated with client read paths, storage server actors, data distribution, ratekeeper commit-cost feedback, TSS comparison, backup/change-feed remnants, audit, and bulk loading or dumping flows.

## Risks and Edge Cases
Changing serialized fields or endpoint ordering can break downgrade compatibility because server-list values are durable. Read request freshness depends on correctly populated `VersionVector` data. Large selector offsets, wrong-shard ownership, and streamed reply backpressure are important behavior boundaries. Obsolete change-feed structures can look dead but are persistence-sensitive. Metric arithmetic can overflow or become misleading if callers mix logical and physical metrics without respecting field semantics.

## Test Signals
Useful signals include simulation read/write and range-read tests, storage relocation and shard-state tests, data distribution metric/split tests, checkpoint and bulk dump workloads, tag throttle/ratekeeper integration tests, serialization compatibility tests across protocol versions, and wrong-shard or TSS comparison simulation coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerInterface.h -->
