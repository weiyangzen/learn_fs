# sources/sync-backup/kopia/repo/blob/gcs/gcs_versioned_test.go

Purpose: live integration tests for GCS versioned/PIT behavior.

Important APIs/types/functions: `bucketOpts`, `TestGetBlobVersionsFailsWhenVersioningDisabled`, `TestGetBlobVersions`, `TestGetBlobVersionsWithDeletion`, `putBlobs`, `createBucket`, `validateBucket`, and `getImmutableBucketNameOrSkip`.

Control flow: tests create or validate buckets with required versioning settings, write multiple versions of blobs, invoke version listing/PIT helpers, and assert correct version visibility and deletion handling. Disabled-versioning tests ensure PIT setup fails with the expected error.

State and persistence behavior: tests create real GCS buckets/objects/generations and may depend on project-level permissions. Versioned objects persist until cleanup.

Dependencies/integration points: exercises GCS bucket creation/validation, object generation listing, PIT read-only wrapping, and deletion timestamp logic. Risks include environment/project permissions, bucket naming conflicts, cloud timestamp precision, and cleanup after failures. These are the main signals for GCS historical view correctness.
