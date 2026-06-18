# sources/user-network-fs/rclone/cmd/archive/files/countwriter.go

Purpose: provides `CountWriter`, an `io.Writer` wrapper used by archive creation to count compressed bytes written. It wraps nil writers as `io.Discard` and tracks count with `atomic.Uint64`.

APIs: `NewCountWriter`, `Write`, and `Count`. `Write` delegates to the wrapped writer and increments by the returned byte count when positive, even if the writer also returns an error. State is the wrapped writer and atomic byte counter. Dependencies are `io` and `sync/atomic`. Risks are limited: concurrent `Write` safety is only as good as the wrapped writer, but count reads are atomic. Tests cover initial count, nil writer, partial writes, errors, and concurrent writes.
