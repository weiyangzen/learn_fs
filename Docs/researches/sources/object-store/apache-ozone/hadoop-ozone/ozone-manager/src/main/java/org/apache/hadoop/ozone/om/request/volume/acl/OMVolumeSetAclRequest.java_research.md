# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeSetAclRequest.java

Purpose: `OMVolumeSetAclRequest` replaces the full ACL list on a volume.

Important APIs and types: It reads `SetAclRequest`, converts the protobuf ACL list to `List<OzoneAcl>`, converts the target object, and injects an `AclOp` that calls `builder.set(acls)`.

Control flow: `preExecute` delegates write-ACL authorization and stamps modification time. The shared base class applies the replacement under the volume lock and calls subclass callbacks. Success creates `SetAclResponse.response`; completion audits with `OMAction.SET_ACL`.

State and persistence behavior: A set operation normally updates the volume table with the new ACL list and transaction update ID. Response persistence writes the changed `OmVolumeArgs`.

Dependencies and integration points: It integrates protobuf ACL lists, `OzoneObjInfo`, shared `OMVolumeAclRequest`, audit logging, and set-ACL metrics.

Risks and test signals: Tests should verify replacing with empty/non-empty ACL lists, idempotent replacement behavior from the ACL builder, audit ACL rendering, and modification time propagation.
