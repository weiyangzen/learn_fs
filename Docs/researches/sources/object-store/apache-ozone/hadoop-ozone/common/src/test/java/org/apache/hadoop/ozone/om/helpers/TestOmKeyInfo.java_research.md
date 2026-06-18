# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyInfo.java

Purpose: tests `OmKeyInfo` protobuf conversion, replication config encoding, hsync metadata detection, expected data generation, copy semantics, ACL/tag mutation effects, and location-list copying.

Important APIs/types/functions: exercises `OmKeyInfo.Builder`, `getProtobuf(ClientVersion)`, `getFromProtobuf`, `withMetadataMutations`, `isHsync`, `copyObject`, `toBuilder`, `setAcls`, `setTags`, and key-location helper classes.

Control flow and state: tests create key info with RATIS and EC replication. RATIS uses factor/type fields, while EC uses `EcReplicationConfig` and omits factor. Copy tests include multipart and non-multipart location groups, compare nested `OmKeyLocationInfoGroup` and `OmKeyLocationInfo`, then mutate ACLs and tags to verify equality changes.

Dependencies and integration points: uses HDDS replication configs, `BlockID`, SCM `Pipeline`, protobuf `KeyInfo`, Ozone ACLs, `ClientVersion`, `OzoneConsts.HSYNC_CLIENT_ID`, and `Time`.

Risks and test signals: protects metadata persistence, replication compatibility, hsync state detection, expected generation tracking, and deep copy of nested block locations. A minor test weakness is that it assigns `clone = key.getKeyLocationVersions().get(i)` instead of the clone list inside the loop, but overall equality checks still cover copy behavior.
