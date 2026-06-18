# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRestart.java

## Purpose
Mini-cluster restart integration tests for core OM metadata operations. It checks that volume, bucket, and key/rename state survives OM and SCM restarts and that duplicate operations still return the expected OM error codes after restart.

## Important APIs and Types
Main class: `TestOzoneManagerRestart`. Important tests are `testRestartOMWithVolumeOperation`, `testRestartOMWithBucketOperation`, and `testRestartOMWithKeyOperation`. It uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneKey`, `OzoneOutputStream`, `OMException`, `BucketLayout.OBJECT_STORE`, and error codes `VOLUME_ALREADY_EXISTS`, `BUCKET_ALREADY_EXISTS`, `PARTIAL_RENAME`, and `KEY_NOT_FOUND`.

## Control Flow
`@BeforeAll` starts a mini-cluster with ACLs enabled, wildcard administrators, a larger SCM Ratis pipeline limit, and object-store default bucket layout. Each test creates metadata, restarts OM and SCM, then re-runs operations against the same client-side object handles or object store. The key test writes one key, attempts a two-key rename where one source is missing, verifies partial rename semantics, restarts, and checks that the successful rename persisted while the missing target remains absent.

## State and Persistence
The tested persistent state is OM RocksDB metadata for volumes, buckets, key entries, and rename results. Restarting both OM and SCM validates that metadata reload and client operation routing still preserve idempotent error behavior. The key test relies on persisted rename side effects despite `PARTIAL_RENAME`.

## Dependencies and Integration Points
This file integrates the object-store Java client, OM metadata layer, SCM restart path, bucket layout defaults, ACL configuration, and key create/rename APIs.

## Risks and Edge Cases
The tests reuse some client-side volume/bucket handles across restart, so failures can reflect handle/proxy behavior as well as server persistence. The key rename test intentionally accepts partial failure and then verifies only the expected successful subset. Random numeric suffixes reduce but do not completely eliminate name collision risk in reused clusters.

## Test Signals
Signals include duplicate volume and bucket creation returning stable error codes after restart, existing metadata being retrievable after restart, renamed key metadata surviving restart, and absent rename inputs remaining absent.
