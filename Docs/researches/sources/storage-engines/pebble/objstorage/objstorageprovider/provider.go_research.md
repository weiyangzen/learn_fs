<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/provider.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/provider.go

Purpose: implements the concrete `objstorage.Provider` coordinating local filesystem objects, optional cold tier, optional shared/remote storage, shared-cache metrics, object metadata cataloging, durability syncs, checkpoint protection, and optional object I/O tracing.

Important APIs and types: `provider` stores settings, tracer, local/remote subsystems, known object metadata, and protected object counts. `Settings` configures local FS, cold tier, cleaner, sync behavior, readahead, and remote cache/shared-storage settings. `ReadaheadConfig` atomically stores informed/speculative modes. Public provider methods include `Open`, `Close`, `OpenForReading`, `Create`, `Remove`, `Sync`, `LinkOrCopyFromLocal`, `Lookup`, `Path`, `Size`, `List`, `Metrics`, and `CheckpointState`; metadata helpers manage known/protected objects.

Control flow: `open` fills defaults, initializes maps, starts tracing if enabled, then initializes local and remote subsystems. `Create` chooses shared remote storage when preferred/configured, otherwise local/cold VFS creation, adds metadata, and wraps tracing. `OpenForReading` looks up metadata, opens local or remote readable, maps missing remote objects to not-exist/corruption errors where appropriate, and wraps tracing. `Remove` removes local files or unreferences shared objects, preserving metadata on retryable removal failures. `LinkOrCopyFromLocal` hard-links/copies locally when possible, otherwise streams through provider create/finish. `CheckpointState` validates and protects listed files, then checkpoints the remote catalog.

State and persistence: `knownObjects` is the in-memory provider catalog initialized from local listings and remote catalog. `Sync` persists local and shared metadata changes. Protected counts prevent remote unref while backing handles or checkpoints need objects retained. Local/cold file durability uses syncing files and provider subsystem syncs.

Dependencies and integration: central implementation of `objstorage.Provider`; depends on local and remote subsystems, `remote.StorageFactory`, `vfs`, `objstorage` contracts, shared cache, tracing, Pebble base file numbering/types, and invariants.

Risks and edge cases: `knownObjects` is keyed only by `DiskFileNum`, with file-type mismatch checked at lookup. Remote removal has TODOs around deferred unref for protected objects. Failed local link/copy or streamed copy paths require callers to handle partially created objects. `isProtected` uses a full lock despite being read-like.

Test signals: object provider behavior is exercised by DB/object-storage integration tests; listed metrics tests use `objstorageprovider.Open` for shared storage and SST writing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/provider.go -->
