# sources/sync-backup/kopia/repo/blob/s3/s3_versioned_test.go

Purpose: validates S3 versioned-object helpers and point-in-time selection primitives against real versioned S3-compatible providers and deterministic in-memory version metadata.

Important APIs/types/functions: tests include `TestGetBlobVersions`, `TestGetDifferentBlobVersions`, `TestSingleBlobVersionsListPrefixes`, `TestListMultipleBlobPrefixes`, `TestGetBlobWithVersion`, `TestGetVersionMetadata`, `TestInfoToVersionMetadata`, `TestGetOlderThan*`, and `TestNewestAtUnlessDeleted*`. Helpers create random blob names/content, put versioned blobs, delete blobs to create delete markers, list versions, compare metadata, and clean all versions by `RemoveObjects`.

Control flow: provider-backed tests open a versioned store from environment credentials, write multiple versions for one or more blob IDs, list exact IDs and prefixes, delete current blobs, and verify historical versions remain accessible. Pure tests build ordered `versionMetadata` slices and check timestamp-based selection and delete-marker handling.

State and persistence behavior: versioned provider tests create multiple object versions under a unique test prefix, then explicitly remove every version and delete marker during cleanup. The suite models provider listing order as blob-name ascending and per-blob versions newest-first.

Dependencies/integration: depends on the S3 provider test credential map, MinIO object metadata, retry helpers, clock, gather buffers, and the point-in-time helpers in adjacent S3 files.

Risks and edge cases: tests depend on versioned buckets being configured correctly and on provider-specific timestamp/version metadata. Comparison intentionally ignores timestamps and `IsLatest` in some places because provider responses differ after newer writes.

Test signals: failures indicate broken exact/prefix version enumeration, inability to read a specific version, incorrect delete-marker handling, wrong conversion from provider object info, or point-in-time selection regressions.
