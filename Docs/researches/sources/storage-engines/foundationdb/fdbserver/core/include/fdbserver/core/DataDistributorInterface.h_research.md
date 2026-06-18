# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataDistributorInterface.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataDistributorInterface.h

Purpose: declares the data distributor RPC interface and request/reply payloads for halting, snapshots, exclusion checks, metrics, range splitting, storage wiggler state, and audit triggers.

Important APIs/types: `DataDistributorInterface`, `PrepareBlobRestoreReply`, `PrepareBlobRestoreRequest`, `HaltDataDistributorRequest`, `GetDataDistributorMetricsReply/Request`, `DistributorSnapRequest`, `DistributorExclusionSafetyCheckReply/Request`, `DistributorSplitRangeRequest`, `StorageWigglerState`, and `GetStorageWigglerStateReply/Request`.

Control flow and state: the interface includes `waitFailure`, halt, snapshot, exclusion check, metrics, split range, storage wiggler, and audit request streams plus locality and `myId`. Request payloads carry reply promises and typed state: blob restore preparation returns success or conflict type; metrics requests carry key range, shard limit, and mid-only flag; snapshot requests carry payload, snapshot UID, and debug ID; split requests carry split points and expect `SplitShardReply`.

State and persistence behavior: the interface is serialized and passed through cluster controller/db-info state, but most state changes occur in the data distributor implementation. Snapshot and blob restore requests can lead to persistent metadata changes outside this header.

Dependencies and integration: depends on cluster interfaces, FDB types, locality, fdbrpc, storage server interfaces, DDMetrics, address exclusions, and audit request declarations. It is the main control surface for external actors talking to DD.

Risks and tests: `GetStorageWigglerStateReply` has timestamp members but serializes only `primary` and `remote`, so consumers must not expect timestamp propagation. File identifiers and field order are wire-compatible contracts. Tests should cover serialization, equality by ID, DD halt, exclusion safety, snapshot fanout, metrics shard limits, split requests, and wiggler state responses.
