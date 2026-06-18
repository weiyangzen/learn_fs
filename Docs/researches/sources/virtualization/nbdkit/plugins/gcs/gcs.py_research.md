# File Research: sources/virtualization/nbdkit/plugins/gcs/gcs.py

This Python plugin exposes Google Cloud Storage objects as an NBD block device, supporting both single-object read-only mode and multi-object writable block mode.

Configuration and capabilities:
- `bucket` and `key` are required.
- `json-credentials` selects a service-account JSON file; otherwise Application Default Credentials are used.
- `size` and `object-size` must be supplied together for writable block mode.
- Single-object mode reads `key` directly and cannot write.
- Block mode maps block `N` to object `<key>/<N as 16-digit hex>`.
- Advertises parallel thread model, multi-connection, trim, zero, fast zero, native FUA, and flush.

Read/write behavior:
- `pread` reads directly from one object or splits across block objects.
- Missing objects read as zeroes.
- `pwrite` requires block mode and rewrites full objects as needed for unaligned writes.
- Whole-object writes upload exactly `cfg.obj_size` bytes.
- `zero` rewrites partial edge blocks and deletes fully covered blocks.
- `trim` deletes only fully covered block objects, rounding inward as NBD permits.

Concurrency:
- `MultiLock` serializes operations per object key while allowing parallel operations on different keys.
- Per-object locking protects read-modify-write sequences for unaligned writes.

Error handling:
- Top-level callbacks translate GCS `GatewayTimeout` and `DeadlineExceeded` to `ETIMEDOUT`.
- Missing objects are treated as sparse zero blocks via `NotFound`.

Embedded tests:
- `LocalTest` uses mocked GCS objects and compares behavior against a temporary reference file for read/write/zero/trim corner cases.
- `RemoteTest` can run against a real bucket when `TEST_BUCKET` and `TEST_JSON_CREDENTIALS` are set.

Risks and edge cases:
- `_put_object` asserts exact object-size uploads; partial logical writes must be expanded before upload.
- Single-object mode is effectively read-only despite `can_write` depending on `obj_size`.
- GCS consistency, latency, and object listing semantics are external dependencies.
- The global config object is mutated by tests and runtime setup.
