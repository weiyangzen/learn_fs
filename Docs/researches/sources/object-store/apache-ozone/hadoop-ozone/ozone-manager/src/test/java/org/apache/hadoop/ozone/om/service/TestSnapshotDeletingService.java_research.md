# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDeletingService.java

Purpose: Unit-tests snapshot deletion decision logic and request batching for moving deleted snapshot table entries. Important APIs and types include `SnapshotDeletingService`, `SnapshotDeletingTask`, `SnapshotInfo`, `TransactionInfo`, `SnapshotMoveKeyInfos`, `OMRequest`, `OMConfigKeys.OZONE_OM_RATIS_LOG_APPENDER_QUEUE_BYTE_LIMIT`, and mocked OM metadata/snapshot managers.

Control flow: `testProcessSnapshotLogicInSDS` parameterizes flushed/unflushed snapshots and active/deleted status, stubs transaction info for deleted snapshots, and asserts `shouldIgnoreSnapshot`. `testSnapshotMoveKeysRequestBatching` creates large deleted-key, renamed-key, and deleted-directory payloads, spies `submitRequest`, calls `submitSnapshotMoveDeletedKeysWithBatching`, and verifies all entries are submitted across multiple bounded requests.

State and persistence behavior: The tests use mocked managers rather than real RocksDB. State is protobuf request payloads, snapshot status fields, transaction info, and captured submitted requests. Integration points are snapshot GC eligibility, SST-filter/flush markers, active versus deleted status, Ratis buffer sizing, and snapshot move-table request structure.

Risks: Large string helpers assume serialized sizes exceed the test buffer and remain below per-batch limits after splitting. Test signals are boolean ignore decisions, total submitted entry count, multiple captured `SnapshotMoveTableKeys` requests, size under limit, and no orphaned deleted/renamed/dir entries.
