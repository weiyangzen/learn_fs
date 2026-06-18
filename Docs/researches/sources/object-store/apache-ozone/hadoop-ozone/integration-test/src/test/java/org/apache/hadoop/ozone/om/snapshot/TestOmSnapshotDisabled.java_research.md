# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotDisabled.java

Purpose: This integration test verifies that snapshot RPCs are rejected when the filesystem snapshot feature flag is disabled. It focuses on the externally visible error contract for create and delete operations.

Important APIs/types/functions: The class uses `MiniOzoneHAClusterImpl`, `OzoneConfiguration`, `ObjectStore`, `OzoneClient`, `OzoneVolume`, `BucketLayout.LEGACY`, `OMConfigKeys.OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, and `OMException.ResultCodes.FEATURE_NOT_ENABLED`. The only test method is `testExceptionThrown`; lifecycle methods are `init` and `tearDown`.

Control flow: `init` sets default bucket layout to legacy, sets DB profile to test, disables `OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, builds a three-OM HA cluster, waits for readiness, and obtains an object-store client. The test creates a volume and bucket, then calls `store.createSnapshot` and `store.deleteSnapshot`, asserting each throws `OMException` with `FEATURE_NOT_ENABLED`.

State and persistence behavior: The test intentionally creates no snapshot state. Its state transition is negative: OM must reject snapshot mutations before any snapshot metadata or checkpoint can be created. Because it runs in HA mode, the feature-disabled path is checked through the same client-to-OM routing used in replicated deployments.

Dependencies and integration points: This test integrates with OM configuration parsing, snapshot request validation, client-side object-store RPCs, and HA MiniOzone startup. It also depends on DB test profile and legacy bucket layout to minimize unrelated layout complexity.

Risks and edge cases: The critical risk is accidentally allowing one snapshot operation while blocking another, or throwing a generic validation error instead of `FEATURE_NOT_ENABLED`. Since only create/delete are covered, list/diff/get-info behavior is covered by broader suites rather than here.

Test signals: Passing signal is exact exception result-code equality for both create and delete snapshot RPCs under a disabled feature flag.
