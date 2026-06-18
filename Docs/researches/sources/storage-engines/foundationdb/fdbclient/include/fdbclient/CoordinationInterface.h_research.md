# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CoordinationInterface.h

Purpose: Defines coordinator-facing client registration interfaces, cluster connection string parsing/storage abstractions, leader discovery messages, protocol info checks, and descriptor mutability checks.

Important APIs/types/functions: `ClientLeaderRegInterface` exposes public get-leader and open-database streams plus descriptor mutability checks and optional hostname. `ClusterConnectionString` parses and serializes `description:id@coords` plus hostnames, exposes cluster key/name, coordinator counts, hostname resolution, and local source IP detection. `IClusterConnectionRecord` abstracts persisted or in-memory connection string records and persistence-on-connect behavior. `LeaderInfo` wraps leader change id, serialized cluster info or forward connection string, and priority bits for process class/exclusion/DC fitness. RPCs include `GetLeaderRequest`, `OpenDatabaseCoordRequest`, `ProtocolInfoRequest/Reply`, and `CheckDescriptorMutableRequest/Reply`. `ClientCoordinators` groups leader registration endpoints, key, and connection record.

Control flow: Clients parse a cluster connection string, create coordinator registration interfaces from addresses/hostnames, ask coordinators for leader info, then open the database through coordination. If leader info has `forward`, clients update their connection record with new coordinators. Leader election compares masked `changeID` priority bits to decide when a leader change is required.

State and persistence behavior: Connection strings are serialized as coordinates/hostnames/key/keyDesc and are persisted through `IClusterConnectionRecord` implementations. `LeaderInfo::changeID` packs priority state into high bits while preserving internal process identity in the rest. `MAX_CLUSTER_FILE_BYTES` bounds cluster file size.

Dependencies and integration points: Depends on FDB types, RPC, locality, commit/cluster interfaces, well-known endpoints, and hostnames. Used by cluster file implementations, NativeAPI connection monitoring, coordinators, cluster controller election, and protocol compatibility probes.

Risks: Connection string parsing rules are strict; accepting duplicate or malformed addresses would break connection or update wrong files. `changeID` bit packing is fragile and tied to `ClusterControllerPriorityInfo` width. Forwarded leader info can mutate durable cluster files. Protocol info reply uses a peer compatibility policy requiring stable interfaces.

Test signals: Valid/invalid connection string parsing; hostname resolution and local source IP detection; file/memory record persistence-on-connect; leader priority bit packing/unpacking and `leaderChangeRequired()` cases; coordinator open-database routing; protocol info compatibility; descriptor mutable checks.
