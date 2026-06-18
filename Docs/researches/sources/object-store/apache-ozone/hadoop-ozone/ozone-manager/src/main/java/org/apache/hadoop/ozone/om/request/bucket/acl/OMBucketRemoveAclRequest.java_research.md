# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketRemoveAclRequest.java

## Purpose

`OMBucketRemoveAclRequest` is the concrete bucket ACL remove operation. It supplies the shared base class with a single ACL removal operation and returns protocol-specific remove responses.

## Important APIs, Types, And Functions

- Constructor parses `RemoveAclRequest.obj` and `acl`, stores the path, object, and singleton ACL list.
- `preExecute(OzoneManager)` adds modification time and user info.
- `onSuccess(...)` emits `RemoveAclResponse.response`.
- `onComplete(...)` audits `OMAction.REMOVE_ACL`, logs missing-ACL/no-op failures distinctly, and increments failure metrics when operation result is false.
- `validateAndUpdateCache(...)` increments remove-ACL metrics, then delegates.

## Control Flow And State

The mutation lambda is `builder.remove(acls.get(0))`. A true result causes the base class to update bucket ACLs, modification time, and update ID in the bucket table cache. A false result represents removing a non-existent ACL and returns a successful protocol envelope with `response=false` but no metadata mutation.

## Dependencies And Integration Points

The class depends on `OzoneAcl`, `OzoneObjInfo`, protobuf remove ACL messages, OM metrics, audit logger, and `OMBucketAclResponse`.

## Risks And Test Signals

Tests should exercise removal of existing and missing ACLs, response boolean semantics, metric increments, audit map ACL formatting, modification time stamping, and inherited behavior for link resolution, lock release, and bucket-not-found errors.
