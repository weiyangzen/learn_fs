<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/zonal_bucket_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/zonal_bucket_test.go

Purpose: reuses file rename tests under a zonal bucket configuration to validate rename semantics with bucket type set to rapid/zonal behavior.

Important APIs/types/functions: suite `ZonalBucketTests` embeds `RenameFileTests` and `fsTest`; `SetupSuite`, `SetupTest`, and `TestZonalBucketTests`.

Control flow: setup disables implicit directories, sets noop metrics/tracing, sets global `bucketType = gcs.BucketType{Zonal: true}`, and mounts. Each test creates explicit folders and objects, then inherited file rename tests run.

State and persistence behavior: fake bucket layout has explicit folder objects and file objects. Rename state should update in the zonal bucket path the same way as regular file rename tests.

Dependencies and integration points: exercises bucket-type-dependent behavior in the filesystem, especially atomic object rename support expected for zonal buckets, while reusing `RenameFileTests`.

Risks: global `bucketType` mutation must be isolated. Zonal buckets have different read/rename optimization paths, so inherited tests catch regressions where rapid bucket behavior diverges from normal POSIX-like rename.

Test signals: all file rename behaviors from `rename_file_test.go` pass with `gcs.BucketType{Zonal: true}` and explicit directory fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/zonal_bucket_test.go -->
