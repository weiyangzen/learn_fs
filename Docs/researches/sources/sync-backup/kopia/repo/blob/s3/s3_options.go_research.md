# sources/sync-backup/kopia/repo/blob/s3/s3_options.go

Purpose: defines persistent options for S3-compatible storage.

Important APIs/types/functions: `Options` with endpoint, bucket, access key/secret/session token, prefix, region, TLS/path-style/hostname/flat-mode flags, storage class, ACL, point-in-time timestamp, user agent prefix, and throttling limits.

Control flow: no functions are implemented here. S3 client construction, validation, PIT behavior, and normal operations live in neighboring S3 files outside this subset plus `s3_pit.go`.

State and persistence behavior: the struct is serialized in repository connection config. Secret access key and session token are marked sensitive. Point-in-time config enables a historical read-only view when versioning is available.

Dependencies/integration points: consumed by S3 provider factory, AWS/S3-compatible clients, throttling, and PIT wrapper. Risks include many provider-specific flags interacting, backward-compatible JSON pressure, credentials/session token handling, and differences between AWS S3 and compatible services. Tests for the full provider are mostly outside this subset; PIT helper behavior is represented here through `s3_pit.go`.
