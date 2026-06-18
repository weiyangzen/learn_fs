<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/buffer.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/record/buffer.go

Purpose: concurrency-safe bytes buffer for recording test data from FUSE handlers.

Important APIs, types, and functions: `Buffer` wraps `bytes.Buffer` with a mutex and implements `io.Writer`; methods are `Write` and `Bytes`.

Control flow: `Write` locks and appends; `Bytes` locks and returns the underlying byte slice.

State and persistence behavior: in-memory buffer only.

Dependencies and integration points: used by `record.Writes` to capture write request data.

Risks and test signals: `Bytes` returns an alias to internal storage after unlocking, so callers must not mutate it concurrently. Tests should cover concurrent writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/buffer.go -->
