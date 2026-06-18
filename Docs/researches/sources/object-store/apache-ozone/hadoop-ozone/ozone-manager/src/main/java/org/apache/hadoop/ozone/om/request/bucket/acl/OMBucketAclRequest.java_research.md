# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketAclRequest.java

## Purpose

`OMBucketAclRequest` is the abstract base for add, remove, and set ACL operations on buckets. It contains shared parsing, link resolution, authorization, locking, ACL mutation, cache update, response callback, and completion/audit flow.

## Important APIs, Types, And Functions

- Constructor accepts an `AclOp`, a functional operation that mutates the bucket ACL builder.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` implements the shared request lifecycle.
- Abstract hooks `getAcls`, `getPath`, `getObject`, `onInit`, `onSuccess`, and `onComplete` let concrete operations supply protocol-specific behavior.
- `onFailure(...)` defaults to an `OMBucketAclResponse` error response.

## Control Flow And State

The method parses the requested object path as a bucket object, resolves bucket links to the real bucket, checks `WRITE_ACL`, acquires the real bucket write lock, loads `OmBucketInfo`, applies the `AclOp`, and only writes a cache update when the operation actually changes ACL state. The update includes transaction update ID and a modification time extracted from the concrete ACL request. It then builds success/failure responses through callbacks, releases locks, and calls completion hooks with audit data that includes the ACL list.

## Dependencies And Integration Points

It depends on `ObjectParser`, `ResolvedBucket`, `AclOp`, `OzoneAcl`, `OzoneObj`, bucket-table cache APIs, `OMBucketAclResponse`, and OM ACL enforcement. Link resolution means ACL updates target the underlying real bucket, not merely a link facade.

## Risks And Test Signals

Risks include wrong request-field probing for modification time, ACL no-op behavior, link resolution correctness, and null volume/bucket lock release if parsing fails before assignment. Tests should cover add duplicate, remove missing, set same list, set different list, bucket link targets, missing bucket, ACL denial, audit ACL contents, and lock detail propagation.
