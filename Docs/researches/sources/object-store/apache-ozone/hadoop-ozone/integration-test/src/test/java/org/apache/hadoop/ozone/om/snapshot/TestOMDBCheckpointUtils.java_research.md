# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOMDBCheckpointUtils.java

## Purpose
Unit tests for `OMDBCheckpointUtils` behavior related to estimated checkpoint tarball size logging and HTTP request parsing for including snapshot data in OM DB checkpoints.

## Important APIs and Types
The class `TestOMDBCheckpointUtils` uses `OMDBCheckpointUtils.logEstimatedTarballSize`, `OMDBCheckpointUtils.includeSnapshotData`, `GenericTestUtils.LogCapturer`, `HttpServletRequest`, JUnit `@TempDir`, and Mockito request stubbing. Helpers include `writeSstFilesToDirectory` and `getExpectedLogLine`.

## Control Flow
`writeSstFilesToDirectory` writes fake `.sst` files with random bytes into the temporary DB directory. `testlogEstimatedTarballSize` captures logs, logs a checkpoint estimate without snapshots, waits for a 100 KB log prefix, then adds the DB directory as a snapshot directory and waits for a 200 KB estimate including 20 SST files and one snapshot. `testIncludeSnapshotData` mocks the request parameter `OZONE_DB_CHECKPOINT_INCLUDE_SNAPSHOT_DATA` as `true` and `false` and asserts boolean parsing.

## State and Persistence
Temporary filesystem state consists of generated `.sst` files under `dbDir`; no Ozone metadata DB is opened. Log output is captured from the `OMDBCheckpointUtils` logger. Request state is mocked in-memory.

## Dependencies and Integration Points
This file covers the snapshot checkpoint utility used by OM DB checkpoint/tarball streaming paths and the HTTP parameter controlling snapshot data inclusion.

## Risks and Edge Cases
The size test only verifies log substrings and uses the same directory as both checkpoint and snapshot input for the second estimate. It does not cover null request parameters, uppercase values, non-SST files, nested snapshot directories, or exact log formatting when snapshots are absent because the expected no-snapshot line is only a prefix.

## Test Signals
Signals include checkpoint size estimation accounting for snapshot SST files and `includeSnapshotData` returning true only when the request parameter is the string `true`.
