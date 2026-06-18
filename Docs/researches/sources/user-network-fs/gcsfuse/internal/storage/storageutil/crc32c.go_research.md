## sources/user-network-fs/gcsfuse/internal/storage/storageutil/crc32c.go

Purpose: Provides a helper for computing GCS-compatible CRC32C checksums.

Important APIs/types/functions: package variable `crc32cTable` uses `crc32.Castagnoli`; `CRC32C(contents []byte) *uint32` returns a pointer suitable for `gcs.CreateObjectRequest.CRC32C`.

Control flow: computes checksum over the supplied byte slice and returns the address of a local checksum value, which safely escapes to the heap.

State and persistence behavior: immutable checksum table is initialized once. No persistence or external state.

Dependencies and integration points: used by tests or callers creating object requests with checksum preconditions. Depends only on Go `hash/crc32`.

Risks: caller receives a mutable pointer; no nil/streaming variant exists for large data.

Test signals: no direct test in this subset, but object creation tests elsewhere can validate server-side checksum behavior.
