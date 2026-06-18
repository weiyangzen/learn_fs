## sources/user-network-fs/gcsfuse/internal/storage/storageutil/md5.go

Purpose: Provides an MD5 checksum helper for object creation requests.

Important APIs/types/functions: `MD5(contents []byte) *[md5.Size]byte` returns `md5.Sum(contents)` as a pointer.

Control flow: one-shot checksum over an in-memory byte slice.

State and persistence behavior: no state beyond returned heap-escaped checksum.

Dependencies and integration points: depends on Go `crypto/md5`; intended for `gcs.CreateObjectRequest.MD5`.

Risks: MD5 may be unavailable or discouraged for security use, but here it is an integrity checksum. Large content requires full byte slice in memory.

Test signals: object attribute tests validate MD5 byte conversion paths, though not this helper directly.
