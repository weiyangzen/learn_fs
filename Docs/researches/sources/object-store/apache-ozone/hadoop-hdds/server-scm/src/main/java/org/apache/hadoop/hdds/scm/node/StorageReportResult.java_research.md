# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StorageReportResult.java

## Purpose
`StorageReportResult` is a small value object returned by storage-report processing to describe aggregate report status and sets of full or failed volumes.

## Important APIs, Types, And Functions
The object stores an `SCMNodeStorageStatMap.ReportStatus`, a set of full `StorageLocationReport`s, and a set of failed `StorageLocationReport`s. Getters expose those fields. The nested package-private `ReportResultBuilder` supports fluent `setStatus`, `setFullVolumeSet`, `setFailedVolumeSet`, and `build`.

## Control Flow
There is no business control flow beyond builder construction. `SCMNodeStorageStatMap.processNodeReport` chooses a status and optional sets, then builds this result.

## State And Persistence Behavior
Instances hold references to the provided sets and do not defensively copy them. There is no persistence and no immutability enforcement; fields are private but not final.

## Dependencies And Integration Points
The class depends on `SCMNodeStorageStatMap.ReportStatus` and `StorageLocationReport`. It is part of the storage-report classification pathway.

## Risks And Edge Cases
Builder fields can be left null. Consumers must handle null full or failed volume sets for statuses that do not set them. Since sets are not copied, later caller mutation can alter the observed result.

## Test Signals
Tests should verify each status combination from `SCMNodeStorageStatMap`, null behavior for omitted sets, and whether callers require defensive copies or null-safe access.
