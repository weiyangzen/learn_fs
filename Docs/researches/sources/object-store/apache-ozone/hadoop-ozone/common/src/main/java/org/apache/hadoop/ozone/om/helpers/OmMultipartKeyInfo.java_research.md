# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartKeyInfo.java

Purpose: Persisted metadata for an in-progress multipart upload.

Important APIs/types/functions: Extends `WithObjectID`, implements `CopyObject`, and persists via `MultipartKeyInfo` protobuf `CODEC`. Fields include upload ID, optional volume/bucket/key/owner, ACLs, creation time, replication config, parent ID, schema version, and a sorted `PartKeyInfoMap`. `PartKeyInfoMap` keeps `PartKeyInfo` values sorted by part number with binary-search get/put. Builder sets all fields. `getProto` and `builderFromProto` handle serialization.

Control flow and state: Schema version controls part storage. Version 0 stores part info inline in `MultipartKeyInfo`; version 1 requires the inline map to be empty because parts are stored in the separate multipart parts table. `addPartKeyInfo` rejects schema version 1 and replaces/positions parts by part number for version 0.

State and persistence behavior: Stored in the OM multipart info table. Object/update/parent IDs and replication config persist with upload metadata. Copy construction reuses immutable ACL and part-map references safely.

Dependencies and integration points: Used by MPU initiate, commit part, complete, abort, and list operations. Depends on `PartKeyInfo` protobuf, replication config, ACL utilities, and object ID base class.

Risks: Equality/hash use upload ID only, so two entries with the same upload ID but different key context compare equal. Schema-version misuse throws at runtime. Builder for schema 1 intentionally drops inline part info from proto.

Test signals: Codec round trips for schema 0 and schema 1, sorted part insertion/replacement, part lookup, schema 1 rejection of inline parts, replication config serialization, object/update/parent ID persistence, and copy-object behavior.
