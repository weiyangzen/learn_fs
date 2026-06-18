# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/snapshot/TestOMSnapshotSetPropertyRequestAndResponse.java

## Purpose
This class validates `OMSnapshotSetPropertyRequest` and `OMSnapshotSetPropertyResponse` for updating snapshot size properties. It focuses on exclusive logical size and exclusive replicated size, plus failure metrics when metadata table reads fail.

## Important APIs and Types
It uses `SetSnapshotPropertyRequest`, `SnapshotSize`, `OMSnapshotSetPropertyRequest`, `OMSnapshotSetPropertyResponse`, `SnapshotInfo`, `Table.KeyValueIterator`, cache `CacheKey`/`CacheValue`, and mocked `OmMetadataManagerImpl`/`Table`.

## Control Flow and State
Setup initializes a random snapshot name prefix and expected sizes of 2000 and 6000. `createSnapshotDataForTest` adds ten snapshots to the snapshot info table cache. `createSnapshotUpdateSizeRequest` iterates current snapshot rows and builds one `SetSnapshotProperty` OM request per snapshot key with the target `SnapshotSize`.

`testValidateAndUpdateCache` runs each request through preExecute, validate, response DB update, and batch commit. It then checks snapshot set-property metrics increased by the number of requests, failure metrics stayed flat, each persisted `SnapshotInfo` row contains the expected exclusive sizes, and each cache value was updated. The failure test replaces the metadata manager's snapshot table with a mock that throws `CodecException` on `get`; every request returns `INTERNAL_ERROR`, success metrics remain unchanged, and failure metrics increase by the request count.

## Dependencies and Integration Points
The tests integrate request protobuf construction, snapshot info table iteration, metadata cache updates, response batch persistence, and snapshot internal metrics.

## Risks and Test Signals
Risks include updating only the DB but not cache, only updating one of the two size fields, partial metric increments, and exception paths returning success. The test signals all of those with cache assertions, persisted iterator checks, statuses, and metrics.
