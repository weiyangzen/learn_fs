# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDirectoryInfo.java

Purpose: Persisted directory metadata for file-system-optimized buckets, keyed by parent object ID and directory name.

Important APIs/types/functions: Extends `WithParentObjectId`. `CODEC` persists `DirectoryInfo` protobuf. Builder sets name, owner, creation/modification time, ACLs, metadata, object/update/parent IDs. Conversion helpers bridge to/from `OmKeyInfo` builders.

Control flow and state: Immutable after build. `getPath` constructs `parentObjectID/name`. `getProtobuf` writes ACLs, metadata, object/update/parent IDs, and optional owner. `builderFromProtobuf` parses all persisted fields.

State and persistence behavior: Stored in OM directory table for FSO layout. Metadata, ACLs, object IDs, and parent IDs are persisted through protobuf codec.

Dependencies and integration points: Integrates with FSO path resolution, directory table updates, key-to-directory conversion, `OzoneAclUtil`, and `KeyValueUtil`.

Risks: Builder from `OmKeyInfo` does not set owner from key info in the visible constructor path, so callers should verify owner expectations. `getPath` is object-ID based, not a user full path.

Test signals: Directory codec round trips, ACL/metadata persistence, conversion to/from `OmKeyInfo`, parent/object ID identity, and FSO path lookup behavior.
