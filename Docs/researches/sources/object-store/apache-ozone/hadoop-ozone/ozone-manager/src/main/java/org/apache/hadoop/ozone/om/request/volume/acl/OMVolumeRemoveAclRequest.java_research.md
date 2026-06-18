# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeRemoveAclRequest.java

Purpose: `OMVolumeRemoveAclRequest` specializes the volume ACL base class to remove one ACL from a volume.

Important APIs and types: It reads `RemoveAclRequest`, stores a singleton `OzoneAcl`, stores an `OzoneObj`, and uses an `AclOp` that calls `builder.remove(acls.get(0))`.

Control flow: `preExecute` performs base ACL authorization and stamps modification time. On success it writes `RemoveAclResponse.response` with the applied/no-op result. Completion logs success or failure and audits with `OMAction.REMOVE_ACL`. It increments remove-ACL metrics before base validation.

State and persistence behavior: If the ACL was present, the base class stages an updated `OmVolumeArgs` in the volume table cache. Removing a non-existing ACL is a no-op response and avoids DB mutation.

Dependencies and integration points: It uses the common volume ACL flow, OM audit logger, metrics, and `OMVolumeAclOpResponse`.

Risks and test signals: Tests should cover removal of present and absent ACLs, modification time only on applied changes, path-derived volume names, and lock release on missing volume.
