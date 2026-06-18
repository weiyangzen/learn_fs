# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/proto/OmStorageProtocol.proto

Purpose: Private unstable protobuf schema for selected OM storage-layer persisted values.

Important APIs/types/functions: Generates `OzoneManagerStorageProtos` under `org.apache.hadoop.ozone.storage.proto`. Defines `OzoneAclInfo` with identity type, name, rights bytes, and ACL scope; `PersistedPrefixInfo` for prefix name, ACLs, metadata, object ID, and update ID; `PersistedUserVolumeInfo` for user-to-volume mappings and IDs; `GlobalStatsValueProto`; `FileSizeCountKeyProto`; and `SnapDiffObjectInfo`.

Control flow, state, and persistence: These messages are persisted in OM metadata tables and consumed by codecs such as `OmPrefixInfo.getCodec()`. Proto2 required/optional/repeated fields define on-disk compatibility. Metadata uses shared `hadoop.hdds.KeyValue` from `hdds.proto`.

Dependencies and integration points: Used by storage helper classes, OM metadata tables, prefix ACL handling, namespace summary/global stats, file-size count keys, and snapshot diff logic.

Risks: Storage proto changes are on-disk compatibility risks. Required fields cannot be omitted in new records. ACL rights bytes and enum mappings must remain compatible with runtime `OzoneAcl`/`IAccessAuthorizer` semantics. The interface is marked private unstable but still affects persisted OM DB content.

Test signals: `TestOmPrefixInfo`, `TestOmPrefixInfoCodec`, and related codec tests validate a subset of storage proto round trips. Broader compatibility should be covered by upgrade and metadata DB tests.
