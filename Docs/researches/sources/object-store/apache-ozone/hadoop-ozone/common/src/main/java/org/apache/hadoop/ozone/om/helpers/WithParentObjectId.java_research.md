<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithParentObjectId.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithParentObjectId.java

## Purpose

`WithParentObjectId` extends `WithObjectID` with a parent object ID used for filesystem-optimized bucket path traversal.

## Important APIs, Types, And Functions

It adds final `getParentObjectID` and a nested abstract `Builder<T>` with `setParentObjectID` and protected `getParentObjectID`.

## Control Flow, State, And Persistence

Subclasses set the parent ID during build. In FSO buckets, each path component has an object ID and links to its parent, allowing table lookups by parent/child rather than full string paths. The base class itself does not serialize; subclasses include parent ID in their protobuf state.

## Dependencies And Integration Points

It depends on `WithObjectID` and is used by directory/key metadata that participate in FSO namespace traversal, rename, delete, and list-status operations.

## Risks And Test Signals

There is no validation that parent IDs are non-negative or correspond to real parents. Tests should cover root/bucket parent IDs, nested directory creation, rename parent changes, protobuf round trips in subclasses, and invalid parent handling upstream.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithParentObjectId.java -->
