# sources/storage-engines/pebble/objstorage/remote/mem.go

Purpose: This file implements an in-memory `remote.Storage` used by tests. It models object creation, deletion, listing, size, and read-after-delete errors without filesystem dependencies.

Important types and functions: `NewInMem` creates an `inMemStore` with a mutex-protected map of object name to `inMemObj`. `ReadObject` returns an `inMemReader` that stores object name and store pointer rather than a data slice, so deletion after open is observed. `CreateObject` returns an `inMemWriter` that buffers until close. `List`, `Delete`, `Size`, `IsNotExistError`, `getObj`, `addObj`, and `rmObj` implement the storage contract.

Control flow: Writers accumulate bytes in a `bytes.Buffer`; `Close` installs the object into the map and nils the store pointer. Writing after close panics under assertion. Reads look up the object on every `ReadAt`; missing object returns a custom not-exist error. Reads past EOF return `io.EOF`. List filters by prefix and panics for non-empty delimiter.

State and persistence: All state is memory-only and lost on `Close`, which zeroes the store. The custom not-exist error forces callers to use `Storage.IsNotExistError` rather than OS-specific checks.

Dependencies and integration: Provider tests and remote readable tests use this storage extensively. It supports shared storage across multiple providers by sharing one store instance.

Risks and test signals: It is not durable and does not simulate network failures, partial writes, or eventual consistency. It does deliberately simulate object disappearance after a reader is opened, which is important for corruption handling tests.
