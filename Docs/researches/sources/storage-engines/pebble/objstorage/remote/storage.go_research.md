# sources/storage-engines/pebble/objstorage/remote/storage.go

Purpose: This file defines Pebble's remote object storage abstraction and related policy/identity types. It is the contract implemented by in-tree test stores and external shared-storage integrations.

Important APIs and types: `Locator` is a redactable storage identifier and implements safe formatting. `StorageFactory` resolves a `Locator` to a `Storage`. `CreateOnSharedStrategy` controls which newly created SSTables should live on shared storage, with `ShouldCreateShared` applying the strategy by LSM level and `SharedLevelsStart`. `Storage` defines object read/create/list/delete/size/not-exist classification. `ObjectReader` defines concurrent `ReadAt` and close. `ObjectKey` and `MakeObjectKey` identify a remote object by locator/name.

Control flow and semantics: `Storage.CreateObject` may buffer until close and callers must treat close errors as significant. `List` returns full names for a prefix; delimiter grouping is optional. `ObjectReader.ReadAt` must not return partial successful results and must allow parallel reads on the same reader.

State and persistence: This file stores no state; it defines the stable interfaces and strategy constants used by provider settings and DB open/compaction policy.

Dependencies and integration: `objstorageprovider` uses `StorageFactory` for locator resolution, `Storage` for shared object operations, `ObjectReader` for remote reads, and `CreateOnSharedStrategy` during table creation. DB open uses `CreateOnSharedNone` to decide minimum format compatibility.

Risks and test signals: Interface semantics are high impact: not-exist classification affects corruption handling, close errors affect object durability, and locator redaction affects logs/errors. Tests exercise in-memory/local implementations and provider shared-object flows.
