# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMOpenKeysDeleteRequest.java

Purpose: verifies `OMOpenKeysDeleteRequest`, the OM background cleanup request that deletes expired open keys from the open-key table cache. The class extends `TestOMKeyRequest` and parameterizes all behavioral tests across `BucketLayout.DEFAULT` and `BucketLayout.FILE_SYSTEM_OPTIMIZED`, so the same cleanup contract is tested for legacy open-key names and FSO open-file names.

Important APIs and types include `OMOpenKeysDeleteRequest.preExecute`, `validateAndUpdateCache`, `DeleteOpenKeysRequest`, `OpenKeyBucket`, `OpenKey`, `OmKeyInfo`, `OMMetrics`, `OMSystemAction.OPEN_KEY_CLEANUP`, and metadata-manager helpers such as `getOpenKeyTable`, `getOpenKey`, and `getOpenFileName`. Helper methods synthesize open keys, add them to the correct table variant, build delete requests from DB key names, and assert table presence through `isExist`.

Control flow: each test creates one or more volumes/buckets, materializes open keys in RocksDB-backed metadata tables, runs `preExecute` to add user info, then calls `validateAndUpdateCache` with a fixed transaction ID. The tests check missing-key deletion, subset deletion across multiple volume/bucket combinations, identical object names with different client IDs, and update-ID filtering where entries newer than the cleanup transaction must remain while equal-or-older entries are deleted.

State and persistence behavior centers on cache deletion markers over the open-key table rather than final batch commit. In DEFAULT layout the DB key is `volume/bucket/key/clientID`; in FSO it is derived from volume ID, bucket ID, parent object ID, file name, and client ID. The request also leaves bucket snapshot used bytes and namespace at zero after cleanup. Metrics tests distinguish submitted open keys from actually deleted keys.

Dependencies and integration points: `OMRequestTestUtils` creates volumes, buckets, open keys, file entries, and optional key-location data. The test relies on `OzoneManager` metrics and audit-message builders from the mocked test harness. It integrates with cleanup-service semantics: stale cleanup input must be idempotent and must not fail if keys were already committed or removed.

Risks covered: deleting by object name without client ID would corrupt concurrent open writes; deleting cache entries with a higher update ID would violate transaction ordering; FSO key-name construction can drift from production metadata paths; audit failures could hide cleanup errors. The explicit failure path spies `updateOpenKeyTableCache` to throw `IOException` and expects `Status.INTERNAL_ERROR` plus failure audit logging.

Test signals: success is `Status.OK`, absent table entries for deleted keys, present entries for kept/newer keys, correct OMMetrics counters, one success audit containing deleted-key counts, and one failure audit on injected cache-update failure.
