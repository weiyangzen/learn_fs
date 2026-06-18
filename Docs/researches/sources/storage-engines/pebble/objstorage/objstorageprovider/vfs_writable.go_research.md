# sources/storage-engines/pebble/objstorage/objstorageprovider/vfs_writable.go

Purpose: This file adapts a local `vfs.File` into an `objstorage.Writable` with buffered writes, sync-on-finish, close/abort lifecycle, and invariant testing that callers tolerate write-buffer mutation.

Important APIs and types: `NewFileWritable` and `newFileBufferedWritable` construct a `fileBufferedWritable` over a `bufio.Writer` and VFS file. Methods implement `Write`, `Finish`, `Abort`, and `StartMetadataPortion`. `firstError` returns the first non-nil error from two operations and is reused by other provider files.

Control flow: `Write` writes into the buffer and in invariant builds sometimes overwrites the caller's byte slice with `0xFF` to enforce the writable contract. `Finish` flushes the buffer, syncs the file if flushing succeeds, closes the file, nils internal fields, and returns the first error. `Abort` closes the file and drops references without syncing. `StartMetadataPortion` is a no-op for normal local files.

State and persistence: Data becomes durable only after successful flush, file sync, and close in `Finish`; directory syncing is handled at provider level through local change counters and `localSync`.

Dependencies and integration: `vfsCreate` wraps newly created local files with this writable, and tests/tools may call `NewFileWritable` directly.

Risks and test signals: Risks include partial flush/sync errors and callers incorrectly reusing mutated input buffers. Provider tests cover normal local writes, local link/copy data validation, and crash behavior through sync.
