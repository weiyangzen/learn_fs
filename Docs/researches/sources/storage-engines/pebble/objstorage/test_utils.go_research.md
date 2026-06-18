# sources/storage-engines/pebble/objstorage/test_utils.go

Purpose: This file provides `MemObj`, a lightweight in-memory implementation of both `objstorage.Writable` and `objstorage.Readable`, for tests and tools that need an object without filesystem or remote-storage setup.

Important types and functions: `MemObj` wraps a `bytes.Buffer` and implements `Finish`, `Abort`, `Write`, `StartMetadataPortion`, `Data`, `ReadAt`, `Close`, `Size`, and `NewReadHandle`. `memObjReadHandle` is a type alias over `MemObj` implementing `ReadHandle` with no-op `Close`, `SetupForCompaction`, and `RecordCacheHit`.

Control flow: Writes append to the buffer and, in invariant builds, sometimes overwrite the input buffer to catch callers that assume a writable preserves it. `Abort` resets the buffer. `ReadAt` bounds-checks and copies from the buffer, returning an error if the read extends past the object size. `NewReadHandle` returns a handle over the same object; no read-before or readahead behavior is implemented.

State and persistence: State is process memory only. `Data` exposes the underlying buffer slice, so callers must treat it as mutable internal storage.

Dependencies and integration: This utility implements the core `objstorage` interfaces and is useful for unit tests that are not concerned with provider metadata, remote cleanup, or VFS durability.

Risks and test signals: Because reads use a generic error rather than `io.EOF`, it is not a perfect substitute for file-backed objects. It is intentionally simple and should not be used to validate readahead, cache, sync, or cleanup behavior.
