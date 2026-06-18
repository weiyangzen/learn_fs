<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithObjectID.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithObjectID.java

## Purpose

`WithObjectID` is a base class for OM metadata objects with immutable object IDs and monotonically increasing update IDs, in addition to metadata inherited from `WithMetadata`.

## Important APIs, Types, And Functions

It exposes final `getObjectID`, final `getUpdateID`, overridable `getObjectInfo`, and the abstract nested `Builder<T>`. The builder supports `setObjectID`, `setUpdateID`, validation, abstract `buildObject`, and final `build`.

## Control Flow, State, And Persistence

Subclasses use the builder to enforce object-ID immutability after initial assignment and prevent update IDs from moving backwards. A special reclaim-block object ID is allowed as an exception. Persistence is done by subclasses that include object/update IDs in protobuf records.

## Dependencies And Integration Points

It depends on Ozone object ID constants and `WithMetadata`. It is used by volume, bucket, key, and directory metadata classes where object identity and transaction update ordering are central to OM tables and FSO traversal.

## Risks And Test Signals

`validate()` calls `buildObject().getObjectInfo()` when reporting update ID errors, which can instantiate an object during validation. Tests should cover initial ID assignment, rejected object ID changes, reclaim-block exception, update ID monotonicity, and subclass error messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithObjectID.java -->
