# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneObj.java

Purpose: Abstract base for ACL-addressable Ozone resources. It carries resource type and store type and defines the path/name accessors required by authorizers and audit logic.

Important APIs and types: Fields `ResourceType` and `StoreType`; static `toProtobuf`; abstract getters for volume, bucket, key, prefix, prefix path viewer, and full path; `toAuditMap`; equality/hash over type fields. Resource types are VOLUME, BUCKET, KEY, PREFIX; store types are OZONE and S3.

Control flow: Construction validates non-null types. `toProtobuf` maps enum names to protocol enums and includes `getPath`. `toAuditMap` emits resource/storage/volume/bucket/key fields in a linked map.

State and persistence behavior: Stores only object identity metadata in memory. Protobuf conversion creates the serialized form used in OM ACL requests and potentially persisted metadata.

Dependencies and integration points: Used by `OzoneObjInfo`, OM ACL APIs, client translator ACL methods, authorizers, audit logs, and protobuf object representation.

Risks: Base equality only compares resource and store type; subclasses must include path fields, as `OzoneObjInfo` does. Enum name alignment with protobuf enums is required by `valueOf`.

Test signals: Protobuf round-trip through `OzoneObjInfo`, audit map contents, enum alignment, and subclass equality including path data.
