# sources/sync-backup/kopia/internal/iocopy/iocopy.go

Purpose: wraps `io.Copy` with reusable 64 KiB buffers to reduce allocation pressure while preserving standard fast paths.

Important APIs/types/functions: `BufSize`, `GetBuffer`, `ReleaseBuffer`, `Copy`, and `JustCopy`. Global buffer storage is protected by a mutex.

Control flow: `Copy` first delegates to `src.(io.WriterTo)` or `dst.(io.ReaderFrom)` when available, matching `io.Copy` fast-path behavior. Otherwise it obtains a shared buffer, defers release, and calls `io.CopyBuffer`. `JustCopy` discards the byte count.

State/persistence behavior: global buffer freelist is process-local and grows when buffers are released. Buffer contents are not cleared before reuse.

Dependencies/integration: used by `fshasher` and likely other streaming paths. It depends only on `io` and `sync`.

Risks/test signals: `ReleaseBuffer` accepts any slice and does not enforce `BufSize`, so misuse can pollute the pool. Because buffers are reused without clearing, callers must not rely on zeroed memory.
