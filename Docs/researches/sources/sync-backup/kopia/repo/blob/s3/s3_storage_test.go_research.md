# sources/sync-backup/kopia/repo/blob/s3/s3_storage_test.go

Purpose: integration-heavy test suite for the S3 provider across real AWS-compatible services, local MinIO, credential modes, TLS modes, object locking, and provider-validation checks.

Important APIs/types/functions: helpers include `startDockerMinioOrSkip`, `getProviderOptions`, `testStorage`, `testPutBlobWithInvalidRetention`, `createClient`, bucket helpers, `createMinioSessionToken`, and the `customProvider` that can force expired STS credentials. Test cases cover provider credentials from environment variables, AWS, AWS STS, MinIO, custom assume-role credentials, retention buckets, invalid credentials, TLS options, and MD5 requirements.

Control flow: most tests construct `Options`, create or discover a bucket, open storage through `New` or `newStorage`, assign a unique prefix, run `blobtesting.VerifyStorage`, assert connection-info round trips, and optionally run `providervalidation.ValidateProvider`. MinIO tests launch Docker containers with deterministic fake credentials. Token expiration toggles a custom provider from valid to expired and back to validate retry/refresh behavior.

State and persistence behavior: tests create temporary prefixes/buckets and clean old data through `blobtesting.CleanupOldData`. Retention tests use locked and unlocked AWS buckets and verify expected failures or successful locked writes. TLS tests generate local certificates or use badssl endpoints to verify custom transports.

Dependencies/integration: depends on Docker, MinIO, AWS/Wasabi environment variables, provider-validation helpers, Kopia blobtesting utilities, TLS test utilities, MinIO STS, and retrying wrappers.

Risks and edge cases: many tests are provider-gated and skipped without credentials or Linux/amd64 Docker support. Fast-failure tests guard against retry loops on bad credentials. TLS tests intentionally contact external badssl hosts and may be network-sensitive.

Test signals: success means the provider satisfies the blob contract under partial/full reads, writes, listing, deletion, connection serialization, STS token refresh, object lock requirements, and TLS customization.
