# sources/storage-engines/pebble/objstorage/objstorageprovider/vfs_readable.go

Purpose: This file adapts a local `vfs.File` into Pebble's `objstorage.Readable` and `ReadHandle` interfaces. It adds dynamic prefetch, optional OS sequential readahead, handle pooling, finalizer leak checks, and preallocated read-handle support.

Important types and functions: `fileReadable` implements `ReadAt`, `Close`, `Size`, and `NewReadHandle`. `vfsReadHandle` implements `ReadAt`, `SetupForCompaction`, `RecordCacheHit`, and `Close`. `NewFileReadable`, `TestingCheckMaxReadahead`, `PreallocatedReadHandle`, and `UsePreallocatedReadHandle` are exported/test helpers. `fileMaxReadaheadSize` is 256 KiB.

Control flow: A new file readable stats the file to cache its size. Read handles initialize speculative readahead mode from `ReadaheadConfig`. `ReadAt` uses an alternate sequential file descriptor if one has been opened; otherwise it consults `readaheadState`. Depending on mode, it either calls `Prefetch` or switches to `vfs.SequentialReadsOption` once max readahead is reached. `SetupForCompaction` switches to informed mode and may immediately reopen sequentially. Cache-hit notifications advance readahead state unless OS-level or no readahead is active.

State and persistence: State is per readable/handle and not persisted. The underlying VFS file remains the source of truth. Pooling reuses handle objects; `PreallocatedReadHandle` avoids allocation for local reads.

Dependencies and integration: Provider local open uses `newFileReadable`. Table/block readers use `ReadHandle`s for point reads and compactions. `ReadaheadConfig` comes from provider settings.

Risks and test signals: Risks include leaked file descriptors, ignoring failed sequential reopen, short reads, and mismatched readahead modes. Invariant finalizers catch unclosed readables/handles. Provider tests exercise local readahead modes and preallocated handles.
