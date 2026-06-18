<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager_test.go

Purpose: unit/integration tests for bucket manager construction and setup against fake storage with mocked storage-layout calls.

Important APIs/types/functions: ogletest suite `BucketManagerTest`; constants `TestBucketName` and `invalidBucketName`; setup with `storage.NewFakeStorageWithMockClient`; tests `TestNewBucketManagerMethod`, `TestSetUpBucketMethod`, `TestSetUpBucketMethod_IsMultiBucketMountTrue`, and missing-bucket variants.

Control flow: setup creates fake storage and configures the mock storage-control client to report hierarchical namespace and zonal location for the test bucket. Tests instantiate `bucketManager` with representative config, call `SetUpBucket`, and assert returned syncer or expected error strings.

State and persistence behavior: fake storage server and mock storage layout are test state. Bucket manager starts GC contexts and wraps fake bucket state, then teardown shuts down fake storage.

Dependencies and integration points: covers `BucketHandle` and `BucketType` storage-layout integration, syncer creation, stat cache config, prefix wrapping through `OnlyDir`, rate limit config, and error propagation from missing buckets.

Risks: tests assert string fragments from storage-layout errors. They do not verify every wrapper layer directly, only that setup completes and syncer is present.

Test signals: construction returns non-nil manager, setup returns non-nil syncer in single and multibucket modes, and missing buckets propagate NotFound storage-layout errors with nil syncer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager_test.go -->
