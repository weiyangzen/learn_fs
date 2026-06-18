# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterInterface.h

Purpose: Defines the cluster controller client-facing RPC interface and request/reply types for opening databases, failure monitoring, status, worker discovery, recovery, shard movement/splitting, and system-data repair.

Important APIs/types/functions: `ClusterInterface` contains request streams for open database, failure monitoring, status, ping, client workers, force recovery, move shard, repair system data, split shard, and trigger audit. `OpenDatabaseRequest` reports client counts, issues, supported versions, max protocol support, and known client info id, then returns `ClientDBInfo`. `FailureMonitoringRequest/Reply` carry self-diagnosed failures and delta-compressed failure status. `StatusRequest/Reply` returns JSON status. Other contracts include `GetClientWorkersRequest`, `ForceRecoveryRequest`, `MoveShardRequest`, `RepairSystemDataRequest`, `SplitShardRequest/Reply`, and `ClusterControllerClientInterface`.

Control flow: Clients/coordinators send `OpenDatabaseRequest` with their last known client info id and wait until `ClientDBInfo` changes. Participants poll failure monitoring using the interval from the previous reply. Management operations target cluster-controller streams and complete by reply promises. `hasMessage()` checks whether any stream has pending input for controller actors.

State and persistence behavior: This file defines wire state. `StatusReply` persists status as a string during serialization and reconstructs `StatusObject` on deserialization, strict in simulation and lenient outside simulation. Open-database request aggregates client version and issue samples but does not itself persist data.

Dependencies and integration points: Depends on FDB types, failure monitor, status JSON, commit and worker interfaces, and client version. Instantiated by `NativeAPI.actor.cpp` and used by cluster controller actors, fdbcli/status clients, and management API paths.

Risks: Stream ordering and adjusted endpoint identity are part of the RPC contract. `OpenDatabaseRequest::serialize()` asserts protocol support for open database. Status JSON parse leniency outside simulation can mask malformed status fields. Force recovery and repair requests are operationally dangerous and require careful caller gating.

Test signals: Open database long-poll behavior; client info change propagation; failure monitoring deltas and timeout intervals; status JSON strict parse in simulation; worker discovery; force recovery/move/split/repair request routing; serialization compatibility for each request/reply.
