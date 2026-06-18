# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyArgs.java

Purpose: Request argument object for key operations such as create/open/commit/read/head, carrying key identity, replication, size, block locations, ACLs, metadata, tags, multipart fields, and conditional update fields.

Important APIs/types/functions: Extends `WithMetadata` and implements `Auditable`. Builder sets volume/bucket/key/owner/data size/replication/location info, multipart upload ID and part number, recursive/head flags, datanode sort flag, latest-version request flag, force container cache refresh, expected data generation, expected ETag, ACLs, tags, and metadata. `toAuditMap`, `toBuilder`, `addLocationInfo`, and `toProtobuf` are primary methods.

Control flow and state: `dataSize` and `locationInfoList` are mutable after build for commit/update flows. `toProtobuf` serializes only the subset needed by `KeyArgs`, including conditional generation/ETag and part number when nonzero; metadata, ACLs, tags, and replication are handled in higher-level request protos or server-side state.

State and persistence behavior: Request state only. It is transformed into `OmKeyInfo` and table updates by OM request handlers.

Dependencies and integration points: Used across OM key RPC request paths, audit logging, multipart commit, and optimistic concurrency checks. Depends on `ReplicationConfig`, `OmKeyLocationInfo`, `AclListBuilder`, `MapBuilder`, and Ozone constants.

Risks: Request object exposes mutable location list references. `toProtobuf` omits some local fields, so callers must not assume every builder field survives a `KeyArgs` round trip. Conditional update fields must be validated by request handlers.

Test signals: Audit map contents, `KeyArgs` serialization for flags and conditional fields, multipart part number handling, mutable location-list update paths, and builder copy behavior.
