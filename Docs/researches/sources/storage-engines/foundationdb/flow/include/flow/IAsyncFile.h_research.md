# sources/storage-engines/foundationdb/flow/include/flow/IAsyncFile.h

## Purpose
`IAsyncFile.h` defines Flow's asynchronous file and filesystem abstraction used by storage engines, simulation, caching, encryption, and platform-specific I/O backends.

## Important APIs, Types, And Functions
`IAsyncFile` declares open flags, reference counting, `read()`, `write()`, `zeroRange()`, `truncate()`, `sync()`, `flush()`, `size()`, `getFilename()`, zero-copy read/release, `debugFD()`, and optional rate control accessors. `IAsyncFileSystem` declares `open()`, `deleteFile()`, `renameFile()`, `incrementalDeleteFile()`, `lastWriteTime()`, global accessors, and sampling lineage access.

## Control Flow
Callers obtain files from `IAsyncFileSystem::filesystem(g_network)->open()`, then issue Future-returning operations. Default `zeroRange()` and incremental delete are implemented out of line; default `flush()` succeeds immediately; unsupported rate control throws.

## State And Persistence Behavior
The interface persists file contents through backend implementations, with durability controlled by `sync()` and delete `mustBeDurable`. Zero-copy reads pin backend memory until released. Open flags encode buffering, locking, atomic create, large pages, no-AIO, cached read-only, and encrypted modes.

## Dependencies And Integration Points
It depends on `flow.h`, `WriteOnlySet`, `IRateControl`, global `INetwork`, and actor lineage sampling. Backends include KAIO/EIO/non-durable/cached/S3/encrypted wrappers.

## Risks And Edge Cases
The destructor comment warns implementations differ on whether pending operations hold references. Read/write buffers must remain valid until futures are ready. Zero-copy callers must always release and avoid overlapping writes. Encrypted mode has read-only or write-only constraints.

## Test Signals
Backend conformance tests for read/write/truncate/sync/delete/rename, pending-operation destruction, zero-copy fallback and release, atomic write-create rename, encrypted flag behavior, rate control, and crash-durability tests are important.
