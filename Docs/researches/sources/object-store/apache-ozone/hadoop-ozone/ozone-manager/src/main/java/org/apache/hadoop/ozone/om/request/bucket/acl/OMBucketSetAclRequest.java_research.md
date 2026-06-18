# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketSetAclRequest.java

## Purpose

`OMBucketSetAclRequest` replaces the full ACL list on a bucket. It adapts the shared `OMBucketAclRequest` lifecycle for multi-ACL set semantics.

## Important APIs, Types, And Functions

- Constructor converts `SetAclRequest.aclList` into a `List<OzoneAcl>`.
- `preExecute(OzoneManager)` stamps modification time and user info.
- The supplied `AclOp` calls `builder.set(acls)`.
- `onSuccess(...)` writes `SetAclResponse.response`.
- `validateAndUpdateCache(...)` increments set-ACL metrics before base validation/update.

## Control Flow And State

When the new ACL list differs from the current bucket ACL builder state, the base class writes a new `OmBucketInfo` cache entry with updated ACLs, modification time, and update ID. If no effective change is made, response boolean is false and bucket update failure metrics are incremented.

## Dependencies And Integration Points

The request integrates with protobuf `SetAclRequest/SetAclResponse`, `OzoneObjInfo`, stream conversion from protobuf ACLs, `OMBucketAclResponse`, and `OMAction.SET_ACL`.

## Risks And Test Signals

Risk is mostly around set semantics and idempotency. Tests should compare empty, identical, reordered, and changed ACL lists; verify response booleans and cache writes; ensure modification time comes from preExecute; and cover inherited bucket link, authorization, and missing-bucket cases.
