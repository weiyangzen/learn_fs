# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartKeyInfo.java

Purpose: tests `OmMultipartKeyInfo` copy, protobuf conversion, replication config preservation, owner/ACL preservation, part-list isolation, and schema-version constraints.

Important APIs/types/functions: exercises builder setters for upload ID, owner, ACLs, creation time, replication config, schema version, and part key info list; `copyObject`, `getProto`, `getFromProto`, `addPartKeyInfo`, and `getPartKeyInfoMap`.

Control flow and state: loops over standalone, RATIS, and EC replication configs for copy and proto tests. It verifies copied part maps are distinct by mutating the original after copying. Schema version 1 rejects adding part info and rejects serializing a legacy part list.

Dependencies and integration points: uses OM protobuf `MultipartKeyInfo`, `PartKeyInfo`, and `KeyInfo`, HDDS replication configs, `OzoneAcl`, and `Time`. This maps directly to multipart upload metadata persisted by OM.

Risks and test signals: catches loss of replication metadata, shallow part-map copies, owner/ACL loss, and invalid mixing of schema-version 1 with legacy part lists.
