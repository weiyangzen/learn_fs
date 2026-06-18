<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorage.go -->
## sources/storage-engines/pebble/objstorage/objstorage.go

Purpose: defines Pebble's object-storage abstraction for immutable files such as SSTables and blob files, including read/write handles, metadata, provider operations, remote backing, and simple file-backed readable support.

Important APIs and types: `Readable`, `ReadHandle`, and `Writable` define object I/O contracts. `ReadBeforeSize` constants communicate readahead/read-before hints. `ObjectMetadata` identifies local, shared, and external objects. `CreatorID`, `SharedCleanupMethod`, `OpenOptions`, `CreateOptions`, `Provider`, `RemoteObjectBacking`, `RemoteObjectBackingHandle`, and `RemoteObjectToAttach` define provider-level management. Helpers include `Copy`, `IsLocalTable`, `IsExternalTable`, `Placement`, `NewSimpleReadable`, and `SimpleReadable`.

Control flow: `ObjectMetadata` methods classify placement and validate required fields. `Copy` loops in 256KiB chunks from a `ReadHandle` to a `Writable`. `Placement` treats provider lookup failures as local to handle disappeared local objects after reopen. `NewSimpleReadable` records file size, wraps a `ReadableFile`, and returns no-op read handles.

State and persistence: the interfaces define durability boundaries: writes become durable at `Writable.Finish`, object create/remove metadata durability requires provider `Sync`, and provider state may include local catalogs or remote metadata. `SimpleReadable` stores file handle and size only.

Dependencies and integration: central dependency for `objstorageprovider`, SST writers/readers, remote storage, shared cache metrics, vfs, and DB file placement metrics.

Risks and edge cases: `Writable.Write` may mutate input slices, which callers must respect. `ReadHandle` disallows parallel `ReadAt` calls. `SimpleReadable.NewReadHandle` returns the same no-op handle pointer, relying on statelessness. Unknown object placement defaults local, which is intentional but can hide catalog misses.

Test signals: provider and DB integration tests indirectly exercise these contracts; no direct tests in the listed file set.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorage.go -->
