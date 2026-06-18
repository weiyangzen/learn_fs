# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ManagementAPI.h

## Purpose
Declares internal management APIs used by fdbcli, tests, and operational actors to inspect and mutate cluster configuration, coordinator quorum, exclusions, process classes, locks, bulk load/dump jobs, audits, healthy zones, snapshots, backup workers, schema validation, and range locks.

## Important APIs, Types, And Functions
Configuration functions read `DatabaseConfiguration` and wait for full replication. `IQuorumChange`, `changeQuorumChecker()`, `changeQuorum()`, `autoQuorumChange()`, and `nameQuorumChange()` manage coordination changes. Exclusion APIs operate by address or locality and distinguish normal vs failed exclusions. Worker/process APIs read workers and set process classes. Lock/version APIs manage database locks and version advancement. Bulk APIs submit, cancel, read, acknowledge, and track bulk load/dump jobs and histories. `BulkLoadStalledTask`, `BulkDumpProgress`, `BulkLoadProgress`, and `BulkDumpOwnerInfo` define status/owner data. Range lock APIs register owners and take/release/find exclusive read locks. Additional APIs manage healthy zones, primary DC waits, connection strings, schema coverage/matching, cluster snapshots, and backup worker enablement.

## Control Flow
Most operations have `Database` wrappers that run one or more transactions, plus lower-level `Transaction*` overloads for callers composing larger management transactions. Management writes generally target system-key metadata, then background data distributor, coordinators, storage servers, or bulk engines observe and act on it. Progress APIs aggregate task metadata into computed status structs with percent, throughput, and ETA helpers.

## State And Persistence Behavior
Durable state lives in FDB system keys: configuration, exclusions, failed/locality lists, locks, bulk job/task/history records, owner records, range lock metadata, healthy-zone keys, and backup worker flags. Some APIs trigger external process behavior, such as snapshots or reboot requests, through cluster interfaces rather than only persisted keys.

## Dependencies And Integration Points
The header depends on generic management APIs, NativeAPI, range locks, read-your-writes transactions, database configuration, and monitor leader types. It integrates with fdbcli, simulation workloads, data distribution, bulk load/dump engines, backup/restore, audit storage, cluster coordination, and schema/status validation.

## Risks And Test Signals
Risks are operational: incorrect exclusions can reduce fault tolerance, quorum changes can make clusters unreachable, range locks can block writes, bulk job metadata can conflict, and lock-aware flags must be used during restore. Test signals should include fdbcli management tests, simulation workloads for quorum/exclusion/recovery, bulk load/dump lifecycle tests, range-lock owner tests, schema validation tests, and failure-injection around partial management transactions.
