# sources/sync-backup/kopia/repo/blob/b2/b2_storage_test.go

Purpose: live integration tests for the B2 storage provider.

Important APIs/types/functions: B2 environment constants, `TestCleanupOldData`, `TestB2Storage`, `TestB2StorageInvalidBlob`, `TestB2StorageInvalidBucket`, and `TestB2StorageInvalidCreds`.

Control flow: tests read B2 bucket/key credentials from environment or skip, construct `b2.Options`, run shared blob storage test suites, clean old test data, and assert invalid configuration failures.

State and persistence behavior: tests create and hide/delete real B2 objects under the configured bucket/prefix. Cleanup relies on B2 listing/deletion behavior.

Dependencies/integration points: validates the B2 provider against Kopia's generic `blobtesting` contract and the external Backblaze API. Risks include provider deprecation, environment skips, cloud flakiness, and hidden versions accumulating. The tests are the only strong end-to-end signal for B2 because the provider has no local mock tests in this subset.
