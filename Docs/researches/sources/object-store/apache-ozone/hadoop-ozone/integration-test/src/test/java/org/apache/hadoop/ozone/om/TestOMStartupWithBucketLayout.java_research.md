# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMStartupWithBucketLayout.java

Purpose: This compact integration test verifies that bucket layout metadata survives OM restarts and remains independent of later changes to the default bucket layout configuration. It covers both default-FSO and default-OBS startup modes.

Important APIs and types: The file uses `MiniOzoneCluster`, `OzoneConfiguration`, `OzoneClient`, `TestDataUtil.createVolumeAndBucket`, `OzoneBucket`, `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, and `BucketLayout` values `FILE_SYSTEM_OPTIMIZED` and `OBJECT_STORE`.

Control flow: Static helpers start a no-datanode mini cluster, restart only the OM, and tear everything down. `testRestartWithFSOLayout` starts with FSO as the default, creates an explicit FSO bucket, restarts and creates a bucket with no requested layout, restarts and creates an explicit OBS bucket, then verifies all layouts across another restart and after changing the default to OBS. `testRestartWithOBSLayout` mirrors the same sequence with OBS as the initial default and later flips the default to FSO.

State and persistence behavior: The persistent state under test is the bucket layout stored in OM metadata. The tests specifically distinguish per-bucket persisted layout from the mutable `OZONE_DEFAULT_BUCKET_LAYOUT` configuration used only when a new bucket request has no explicit layout.

Dependencies and integration points: It integrates OM startup/restart, bucket creation request handling, client-side `OzoneBucket` layout reads, and the default bucket layout config path. Running without datanodes keeps the scope on OM metadata rather than key IO.

Risks: The class uses static cluster/client fields and manual `try/finally` teardown, so failed startup can affect later tests if cleanup is skipped. It does not inspect raw DB rows; it verifies through client-visible bucket metadata.

Test signals: Signals are exact `BucketLayout` equality for explicit FSO buckets, default-created buckets, explicit OBS buckets, and previously created buckets after multiple restarts and after changing the default layout.
