# sources/sync-backup/kopia/repo/blob/gcs/gcs_storage_test.go

Purpose: live integration tests for normal GCS storage behavior and invalid setup.

Important APIs/types/functions: GCS environment constants, `TestCleanupOldData`, `TestGCSStorage`, `TestGCSStorageInvalid`, `gunzip`, `getEnvVarOrSkip`, `getCredJSONFromEnv`, `mustGetOptionsOrSkip`, and `getBlobCount`.

Control flow: helpers read bucket/project/credential environment variables, decode gzipped credential JSON when present, build `gcs.Options`, and run shared blob testing suites. Cleanup removes old data from the configured bucket/prefix. Invalid tests assert failures for incorrect setup.

State and persistence behavior: tests create/list/delete real GCS objects. Cleanup and counts operate against the live bucket.

Dependencies/integration points: validates GCS provider integration with generic blob tests, credential handling, and cloud API behavior. Risks include skipped coverage when env vars are absent, cloud latency/quota, and retained objects after failures. It complements dedicated immutability and versioned tests.
