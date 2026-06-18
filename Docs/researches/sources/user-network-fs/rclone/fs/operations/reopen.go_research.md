# Research: sources/user-network-fs/rclone/fs/operations/reopen.go

## sources/user-network-fs/rclone/fs/operations/reopen.go

Purpose: implements `ReOpen`, an `io.ReadSeekCloser`/`io.ReaderAt` wrapper around `fs.Object.Open` that retries failed reads by reopening the object at the current offset. APIs include `AccountFn`, `NewReOpen`, convenience `Open`, `Read`, `ReadAt`, `Seek`, `Close`, `SetAccounting`, and `DelayAccounting`.

Control flow records base open options, strips hash options for nonzero-range reopen attempts, tracks optional range/seek starts and ends, and mutates a stored `fs.RangeOption` before reopening. `Read` serializes through `mu`, applies pending seeks, fills the caller buffer, reopens on retryable read errors, and accounts bytes after optional delayed full-data reads. `ReadAt` serializes separately, seeks, reads, then restores position. State is in-memory offsets, retry counters, current reader, open/error flags, and accounting counters; no persistence. Dependencies include `fs.OpenOption`, `fserrors`, and object size semantics. Risks include mutable option aliasing, unknown-size seek-end behavior, sticky errors after failures/close, serialized `ReadAt` rather than true parallel reads, and exact retry-count semantics.
