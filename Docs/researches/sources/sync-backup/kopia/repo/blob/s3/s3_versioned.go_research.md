# sources/sync-backup/kopia/repo/blob/s3/s3_versioned.go

Purpose: adds version-listing support for S3 buckets with object versioning, exposing helpers used by point-in-time storage and version-aware tests.

Important APIs/types/functions: `versionMetadata` extends `blob.Metadata` with `IsLatest`, `IsDeleteMarker`, and provider `Version`. Methods are `IsVersioned`, `getBlobVersions`, `listBlobVersions`, private `list`, `toBlobID`, and `infoToVersionMetadata`.

Control flow: `IsVersioned` asks S3 for bucket versioning and returns `Enabled()`. `getBlobVersions` calls `list` with exact-key matching and converts no-result into `blob.ErrBlobNotFound`. `listBlobVersions` calls the same `list` with recursive prefix listing. `list` sets `WithVersions`, consumes MinIO object info from a channel, stops early on exact-key mismatch, converts each object to `versionMetadata`, and wraps callback/list errors.

State and persistence behavior: this file does not persist new state; it observes S3's versioned object history, including delete markers. Object names are stripped of the configured Kopia prefix when surfaced as blob IDs.

Dependencies/integration: used by `s3_pit.go`/point-in-time behavior and tests that inspect historical versions. It depends on MinIO `ListObjects` with `WithVersions` and the S3 provider's object-name mapping.

Risks and edge cases: exact-match mode relies on S3 listing order with prefix and stops when a different key appears. Delete markers are represented as zero-length metadata with marker flags. Provider versioning semantics can differ between AWS and S3-compatible services.

Test signals: `s3_versioned_test.go` verifies exact blob-version listing, prefix listing, delete-marker behavior, metadata conversion, historical-version reads, and version ordering across S3 and Wasabi versioned providers.
