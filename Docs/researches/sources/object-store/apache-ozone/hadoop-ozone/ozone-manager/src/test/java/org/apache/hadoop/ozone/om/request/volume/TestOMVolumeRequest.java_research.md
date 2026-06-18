# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/volume/TestOMVolumeRequest.java

## Purpose
This is the base fixture for volume request tests. It constructs a mocked `OzoneManager`, real temporary `OmMetadataManagerImpl`, metrics, audit logger, configuration, and helper request builder shared by create, delete, set-owner, set-quota, and ACL tests.

## Important APIs and Types
It uses JUnit `@TempDir`, Mockito, `OzoneConfiguration`, `OMMetrics`, `OMMetadataManager`, `OmMetadataManagerImpl`, `OMLayoutVersionManager`, `AuditLogger`, `AuditMessage`, `OmConfig`, `OzoneAcl`, `CreateVolumeRequest`, `VolumeInfo`, and `OMRequest`.

## Control Flow and State
`setup` creates an `OzoneManager` mock, a real `OzoneConfiguration`, registers metrics, points OM DB dirs to the temp folder, instantiates metadata manager, and stubs OM getters for metrics, metadata manager, max user volume count, layout version manager, audit logger, configuration, and object config. The audit logger is mocked to ignore writes. `stop` unregisters metrics and clears inline mocks.

The static `createVolumeRequest` helper constructs a `VolumeInfo` with volume, admin, owner, and one ACL converted to protobuf, wraps it in `CreateVolumeRequest`, and then an `OMRequest` with random client ID and `CreateVolume` command type.

## Dependencies and Integration Points
Every volume request test in this subset depends on this fixture for realistic metadata persistence and common OM stubs. It integrates the OM configuration object used by request code and the metadata manager's RocksDB-backed tables.

## Risks and Test Signals
Fixture risks include stale OM stubs causing false failures or metrics leaks across tests. `stop` and Mockito clearing reduce cross-test contamination. The helper controls the shape of all create-volume requests in dependent tests.
