# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeAclRequest.java

Purpose: `OMVolumeAclRequest` is the shared implementation for volume ACL add, remove, and set requests.

Important APIs and types: It extends `OMVolumeRequest`, accepts an `AclOp`, defines abstract callbacks for request-specific ACL extraction and response construction, and uses `OmVolumeArgs.Builder.acls()`.

Control flow: `preExecute` checks WRITE_ACL against the target volume and emits action-specific audit records on failure. `validateAndUpdateCache` increments volume update metrics, acquires the volume lock, loads volume metadata, applies the injected ACL operation, stamps modification time from the concrete protobuf request when a change occurs, stages a volume table cache entry, then calls subclass success/failure/completion callbacks.

State and persistence behavior: Successful changed ACLs update only the volume table with a new update ID. Add-existing or remove-missing cases can return success responses with `aclApplied=false` and no cache write.

Dependencies and integration points: It integrates `AclOp`, OM ACL authorization, volume metadata helpers, audit maps from `OzoneObj`, and `OMVolumeAclOpResponse`.

Risks and test signals: Risks include `getAddAclRequest()`/`getSetAclRequest()`/`getRemoveAclRequest()` access patterns depending on protobuf defaults and correct no-op handling. Tests should cover changed and unchanged ACLs, missing volume, audit maps, modification time, and metric failure increments.
