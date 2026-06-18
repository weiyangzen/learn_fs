<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/BucketNameSpace.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/BucketNameSpace.java

## Purpose

`BucketNameSpace` defines the bucket-side namespace boundary for an Ozone tenant. It can map a tenant namespace to one or more top-level Ozone objects such as volumes.

## Important APIs, Types, And Functions

The interface declares `getBucketNameSpaceID`, `getBucketNameSpaceObjects`, `addBucketNameSpaceObject`, `getSpaceUsage`, `setQuota`, and `getQuota`.

## Control Flow, State, And Persistence

There is no implementation in the interface. Implementations decide how namespace objects are represented, how usage is measured, and how quotas are enforced.

## Dependencies And Integration Points

It depends on `OzoneQuota`, `SpaceUsageSource`, `OzoneObj`, and HDDS annotations. `SingleVolumeTenantNamespace` is the concrete implementation in this subset.

## Risks And Test Signals

The interface permits multi-volume future implementations, so callers should not assume exactly one object. Tests should cover namespace object addition, quota usage, public bucket naming expectations, and tenant bucket isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/BucketNameSpace.java -->
