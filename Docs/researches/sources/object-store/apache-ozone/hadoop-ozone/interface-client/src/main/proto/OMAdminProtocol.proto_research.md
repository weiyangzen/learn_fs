# sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OMAdminProtocol.proto

Purpose: Private unstable protobuf/gRPC admin protocol for Ozone Manager administrative operations.

Important APIs/types/functions: Generates `org.apache.hadoop.ozone.protocol.proto.OzoneManagerAdminProtocolProtos`. Defines `OMConfigurationRequest/Response`, `OMNodeInfo`, `NodeState`, `DecommissionOMRequest/Response`, `CompactRequest/Response`, `TriggerSnapshotDefragRequest/Response`, and service `OzoneManagerAdminService`.

Control flow, state, and persistence: RPC methods are request/response envelopes. `getOMConfiguration` returns in-memory OM nodes and nodes from reloaded configuration. `decommission` removes an OM by node id/address. `compactDB` requests compaction of a named OM DB column family. `triggerSnapshotDefrag` can run synchronously or no-wait based on `noWait`.

Dependencies and integration points: Integrated with generated gRPC stubs from the interface-client module, admin CLI, OM HA administration, RocksDB column family management, and snapshot-defrag code. Uses proto2 required/optional semantics.

Risks: The interface is private and unstable but still a wire contract for admin clients. Field-number reuse or required-field changes can break rolling upgrades or mixed client/server versions. `CompactRequest.columnFamily` is stringly typed, so callers must align with OM DB table names. Snapshot defrag is operationally sensitive and may be long-running.

Test signals: No direct proto tests in this module. Downstream admin and OM integration tests should cover service implementations and compatibility plugin should catch incompatible schema edits.
