# sources/sync-backup/kopia/repo/blob/readonly/readonly_storage.go

Purpose: wraps any blob storage to prevent mutations while allowing reads and metadata/list/capacity operations.

Important APIs/types/functions: `ErrReadonly`, `readonlyStorage`, `GetCapacity`, `IsReadOnly`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `Close`, `ConnectionInfo`, `DisplayName`, `FlushCaches`, and `NewWrapper`.

Control flow: read-like methods delegate directly to the base storage. `PutBlob` and `DeleteBlob` always return `ErrReadonly`. `IsReadOnly` returns true regardless of the base. Other lifecycle/introspection calls are delegated.

State and persistence behavior: the wrapper itself stores only the base storage reference and does not mutate blob state. It prevents write/delete through this interface, but cannot prevent mutation through other references to the base storage.

Dependencies/integration points: used by point-in-time wrappers for Azure/GCS and any read-only repository mode. Risks include `ExtendBlobRetention` not being overridden in this file; behavior depends on `DefaultProviderImplementation` or interface embedding for unsupported methods. There are no direct tests in this subset, but PIT tests exercise read-only wrapping indirectly.
