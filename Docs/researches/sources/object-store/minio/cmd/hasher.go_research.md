<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/hasher.go -->
# sources/object-store/minio/cmd/hasher.go

## Purpose
Provides small helper functions for MD5 and SHA-256 sums and hex-encoded hashes.

## Important APIs, types, and functions
- `getSHA256Hash` returns hex-encoded SHA-256.
- `getSHA256Sum` returns raw SHA-256 bytes using MinIO's internal SHA-256 implementation.
- `getMD5Sum` returns raw MD5 bytes.
- `getMD5Hash` returns hex-encoded MD5.

## Control flow
Each sum function constructs a hash, writes the full input byte slice, and returns the digest. Hash functions hex-encode the corresponding sum.

## State and persistence behavior
No state or persistence. Outputs are deterministic functions of input bytes.

## Dependencies and integration points
Uses Go `crypto/md5`, `encoding/hex`, and MinIO internal SHA-256 package. These helpers are likely consumed by ETag, checksum, metadata, and test code elsewhere in `cmd`.

## Risks and edge cases
MD5 is not collision-resistant and should only be used for S3 compatibility/integrity semantics, not new security decisions. Functions ignore write errors because hash writers never fail.

## Test signals
No direct tests in this group. Expected coverage is through checksum, ETag, and authentication/signature tests that compare known digests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/hasher.go -->
