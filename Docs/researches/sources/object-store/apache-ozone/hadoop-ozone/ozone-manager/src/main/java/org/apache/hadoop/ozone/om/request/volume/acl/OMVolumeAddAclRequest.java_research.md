# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeAddAclRequest.java

Purpose: `OMVolumeAddAclRequest` specializes `OMVolumeAclRequest` to add one ACL to a volume.

Important APIs and types: The constructor reads `AddAclRequest`, converts the protobuf ACL with `OzoneAcl.fromProtobuf`, converts the object with `OzoneObjInfo.fromProtobuf`, and derives the volume name from `obj.getPath().substring(1)`.

Control flow: `preExecute` delegates authorization to the base class and stamps `modificationTime`. The injected `AclOp` calls `builder.add(acls.get(0))`. Success sets `AddAclResponse.response` to whether the ACL was applied; failure returns an error `OMVolumeAclOpResponse`. `validateAndUpdateCache` increments add-ACL metrics before delegating.

State and persistence behavior: When the ACL is newly added, the volume table cache gets updated through the base class and response persistence writes `OmVolumeArgs`.

Dependencies and integration points: It integrates volume ACL protobufs, `OzoneObjInfo` path handling, `OMAction.ADD_ACL` audit, and OzoneManager metrics.

Risks and test signals: Risks include path parsing assumptions and add idempotence. Tests should assert duplicate ACL no-op response, modification time propagation, audit action, and table update only when applied.
