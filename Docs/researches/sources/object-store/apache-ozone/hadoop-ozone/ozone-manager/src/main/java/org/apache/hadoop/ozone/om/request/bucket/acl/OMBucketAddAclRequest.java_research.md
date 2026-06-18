# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketAddAclRequest.java

## Purpose

`OMBucketAddAclRequest` is the concrete bucket ACL add operation. It wraps the shared `OMBucketAclRequest` flow with single-ACL extraction, `AddAclResponse`, add-specific metrics, and add-specific audit/logging.

## Important APIs, Types, And Functions

- Constructor converts the protobuf object to `OzoneObjInfo`, stores its path, and converts the protobuf ACL to a singleton `OzoneAcl` list.
- `preExecute(OzoneManager)` stamps current modification time and user info.
- `onSuccess(...)` writes `AddAclResponse.response` and sets top-level success to the operation result.
- `validateAndUpdateCache(...)` increments `incNumAddAcl()` before delegating to the base implementation.

## Control Flow And State

The actual mutation is provided to the base class as `builder.add(acls.get(0))`. If the ACL is new, the base class writes an updated bucket cache entry. If the ACL already exists, no cache entry is written, the response carries `response=false`, and completion increments bucket update failure metrics.

## Dependencies And Integration Points

It integrates with protobuf `AddAclRequest/AddAclResponse`, `OzoneAcl`, `OzoneObjInfo`, `OMBucketAclResponse`, and `OMAction.ADD_ACL` audit logging.

## Risks And Test Signals

Tests should verify modification time is used only on successful mutations, duplicate adds return false without state changes, add metrics increment independently from bucket update metrics, audit output includes the ACL string, and link/missing-bucket/ACL-denied cases inherit base behavior.
