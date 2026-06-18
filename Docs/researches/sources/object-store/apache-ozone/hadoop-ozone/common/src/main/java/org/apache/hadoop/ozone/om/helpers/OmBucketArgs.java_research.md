# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmBucketArgs.java

Purpose: Request argument object for bucket create/modify operations, carrying bucket identity, versioning, storage type, quotas, encryption key, default replication, owner, metadata, tags, and audit fields.

Important APIs/types/functions: Extends `WithMetadata` and implements `Auditable`. Builder validates volume and bucket names and tracks whether quota fields were explicitly set. `toAuditMap` emits user-visible audit fields. `getProtobuf`, `builderFromProtobuf`, and `getFromProtobuf` map to `BucketArgs`.

Control flow and state: Quota values default to `QUOTA_RESET` unless their explicit-set flags are true. Proto serialization writes optional fields only when meaningful: version/storage/owner/encryption/default replication/tags, and quotas only when set to positive values or reset. The deprecated bucket encryption setter ignores non-null entries with null key names.

State and persistence behavior: Primarily RPC/request state. When accepted by OM, fields feed persisted `OmBucketInfo`.

Dependencies and integration points: Used by bucket create/set-property flows, audit logging, and protobuf request handling. Depends on `DefaultReplicationConfig`, `StorageType`, `BucketEncryptionKeyInfo`, `MapBuilder`, `KeyValueUtil`, and `OMPBHelper`.

Risks: Audit quota condition relies on operator precedence and can include reset values even when explicit flags are false. Builder requires tags object, but the field is always initialized. Null optional fields require downstream defaults.

Test signals: Proto round trips for optional quotas, reset quotas, encryption key, default replication, tags, metadata, owner, and audit map contents.
