## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyAclRequest.java

**Purpose:** Verifies object-store key ACL add, remove, and set request handling for existing keys in the OM key table. It is the base class reused by the FSO variant.

**Important APIs/types/functions:** Uses `OMKeyAclRequest` plus concrete `OMKeyAddAclRequest`, `OMKeyRemoveAclRequest`, and `OMKeySetAclRequest`; protobuf requests `AddAclRequest`, `RemoveAclRequest`, `SetAclRequest`; `OzoneObjInfo` for KEY resources; and `OzoneAcl.parseAcl` / `OzoneAcl.toProtobuf`. `addKeyToTable` seeds the key table through `OMRequestTestUtils.addKeyToTable`.

**Control flow:** Each test creates volume, bucket, and key metadata; builds an ACL protobuf request; runs `preExecute` and verifies the generated modification time increases from the original request; then calls `validateAndUpdateCache` and checks the returned `OMResponse` status and typed ACL response. The remove test first adds the ACL through the production add path, then removes it.

**State and persistence behavior:** Assertions read `omMetadataManager.getKeyTable(getBucketLayout())` by ozone key. Successful add/set mutates the key's ACL list in cache/table state, while remove empties it. The tests confirm the key identity remains unchanged after ACL mutation.

**Dependencies and integration points:** Relies on the shared `TestOMKeyRequest` mock OzoneManager, bucket layout hook, and audit/metadata setup. It exercises ACL request classes in `org.apache.hadoop.ozone.om.request.key.acl` and validates integration with key metadata mutation rather than standalone ACL storage.

**Risks:** Main risks are ACL operations silently not updating modification time, mutating the wrong key table under layout overrides, duplicate add/remove behavior diverging from expected ACL list semantics, or losing key identity while replacing ACL lists.

**Test signals:** OK statuses, non-null typed ACL responses, modified ACL list sizes/content, and key-name equality before/after mutation indicate correct request behavior.
