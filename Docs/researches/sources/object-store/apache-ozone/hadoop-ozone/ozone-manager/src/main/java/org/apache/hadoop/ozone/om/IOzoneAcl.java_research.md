# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/IOzoneAcl.java

## Purpose

`IOzoneAcl` is the common OM interface for retrieving ACLs and checking access on Ozone objects.

## Important APIs and Types

- `getAcl(OzoneObj obj)` returns `List<OzoneAcl>` and may throw `IOException`.
- `checkAccess(OzoneObj ozObject, RequestContext context)` returns whether the request context has access and may throw `OMException`.

## Control Flow

This is an interface; concrete behavior is implemented by managers such as `BucketManagerImpl` and key/volume managers.

## State and Persistence

The interface holds no state. Implementations usually read persisted OM metadata ACL lists.

## Dependencies and Integration Points

It depends on `OzoneAcl`, `OzoneObj`, `RequestContext`, and `OMException`. It is the shared ACL contract for OM managers.

## Risks and Edge Cases

Implementations must consistently handle object resource types, bucket links, missing metadata, and exception types. Mismatched semantics can lead to authorization inconsistencies.

## Test Signals

Contract tests should exercise positive/negative access checks, invalid object types, missing resources, and exception mapping for each implementing manager.
