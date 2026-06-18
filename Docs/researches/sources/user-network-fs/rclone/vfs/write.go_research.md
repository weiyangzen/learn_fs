# sources/user-network-fs/rclone/vfs/write.go

## Purpose
Implements `WriteFileHandle`, the non-cache streaming write handle for VFS files. It writes sequential data to the remote via an `io.Pipe` and `operations.Rcat`.

## APIs, Flow, And State
`newWriteFileHandle` creates the handle, adjusts symlink remotes with `fs.LinkSuffix`, initializes condition state, and registers the writer on the `File`. `safeToTruncate` decides whether opening is allowed without cached random-write support. `openPending` lazily starts a goroutine that uploads from a pipe, truncates local VFS size state, and adds the object to the directory. `WriteAt` waits briefly for in-sequence offsets, rejects seeks with `ESPIPE`, lazily opens, writes to the pipe, updates offset and file size, and broadcasts waiters. `Close`, `Flush`, and `Release` converge through `close`, which finalizes the pipe, waits for upload result, updates the VFS object, or removes failed placeholder files. Reads are rejected with `EPERM`; `Truncate` only allows truncating to the current offset.

## Dependencies And Integration
Depends on `operations.Rcat`, `File` writer tracking and size/object updates, VFS `WriteWait`, symlink suffix handling, and error constants from the VFS package. It is used when cache mode does not supply read/write cached handles.

## Risks And Test Signals
Risks are sequential-write enforcement, error propagation from async upload to close/flush, zero-byte creates on remotes that reject empty files, and race behavior for `Flush` versus `Release`. `write_test.go` covers method behavior, readonly remote errors, sequential `WriteAt`, flush/release semantics, open-writer modtime, and reading back zero/nonzero writes.
