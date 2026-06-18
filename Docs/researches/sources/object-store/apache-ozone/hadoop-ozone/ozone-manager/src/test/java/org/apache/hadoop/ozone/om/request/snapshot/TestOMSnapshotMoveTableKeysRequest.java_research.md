# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/snapshot/TestOMSnapshotMoveTableKeysRequest.java

## Purpose
This class validates `OMSnapshotMoveTableKeysRequest`, which moves deleted-key, deleted-directory, and renamed-key records into snapshot-scoped tables during snapshot cleanup. The constructor calls `super(true)`, enabling snapshot checkpoint behavior in the base fixture.

## Important APIs and Types
It uses `moveSnapshotTableKeyRequest`, `deleteSnapshotRequest`, `SnapshotUtils.getSnapshotInfo`, `SnapshotInfo`, `OmKeyInfo`, `Pair<String, List<OmKeyInfo>>`, `HddsProtos.KeyValue`, `OMClientResponse`, and OM snapshot internal metrics. Result-code assertions target `INVALID_KEY_NAME`, `INVALID_REQUEST`, and `INVALID_SNAPSHOT_ERROR`.

## Control Flow and State
`createSnapshots` creates one or two checkpointed snapshots and loads their `SnapshotInfo`. `deleteSnapshot` runs a delete request and reloads snapshot state. `testValidateAndUpdateCacheWithNextSnapshotInactive` deletes the next snapshot before moving keys for the previous snapshot; validation fails with `INVALID_SNAPSHOT_ERROR` and increments failure metrics.

PreExecute validation tests build mixed valid/invalid deleted key, deleted dir, and rename-key lists. Invalid volume/bucket prefixes must throw `INVALID_KEY_NAME`. Duplicate entries in any moved-key category must throw `INVALID_REQUEST`. `testPreExecuteWithInvalidNumberKeys` also proves preExecute filters invalid empty entries and rename pairs missing values before the validated request is processed. The successful path creates valid deleted key, deleted dir, and rename lists for the snapshot bucket, runs preExecute and validate, then asserts an `OK` response and one additional move-table-keys metric event.

## Dependencies and Integration Points
The class depends heavily on helper methods from `TestSnapshotRequestAndResponse` that synthesize deleted key lists, deleted dir lists, and rename key mappings. It integrates snapshot chain state, snapshot ID targeting, OM request protobuf normalization, and internal cleanup metrics.

## Risks and Test Signals
Risks include moving records from a different bucket into a snapshot, duplicate moves corrupting cleanup state, accepting malformed rename pairs, and processing against inactive neighbor snapshots. The tests signal these through precise exception result codes, response statuses, and metric increments.
