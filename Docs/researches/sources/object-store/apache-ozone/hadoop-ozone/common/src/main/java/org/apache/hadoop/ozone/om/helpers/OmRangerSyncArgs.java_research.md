<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRangerSyncArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRangerSyncArgs.java

## Purpose

`OmRangerSyncArgs` carries the target Ranger service version for a manual or background Ranger synchronization request.

## Important APIs, Types, And Functions

The class exposes `getNewSyncServiceVersion()` and a nested `Builder` with `setNewSyncServiceVersion()` and `build()`. `newBuilder()` is the construction entry point used by protocol or command code.

## Control Flow, State, And Persistence

Instances are immutable after construction and are request arguments only. The builder stores a primitive long, then creates the final object. No persistence occurs in this class; OM/Ranger sync state is maintained by the service that consumes the version.

## Dependencies And Integration Points

It depends on `java.util.Objects` and integrates with `OzoneManagerProtocol.triggerRangerBGSync`-adjacent request handling and any OM internal Ranger sync executor that needs a service-version target.

## Risks And Test Signals

`Objects.requireNonNull(newServiceVersion, ...)` boxes a primitive long and therefore never rejects an unset builder value; omitted values become `0`. Tests should cover default builder behavior, explicit version propagation, and rejection or interpretation of version zero by the consuming layer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRangerSyncArgs.java -->
