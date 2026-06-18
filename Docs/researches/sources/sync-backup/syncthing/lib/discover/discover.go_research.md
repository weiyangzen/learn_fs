## sources/sync-backup/syncthing/lib/discover/discover.go

Purpose: Declares discovery interfaces and shared cache entry structure.

Important APIs/types/functions: `Finder`, `CacheEntry`, `FinderService`, and `AddressLister`.

Control flow: No implementation logic; these contracts define lookup, error reporting, string identity, cache exposure, service lifecycle, and address-list sources.

State and persistence: `CacheEntry` includes exported addresses and unexported timing/found/instance metadata used by package internals.

Dependencies and integration points: Used by connection service for `discover.Finder`, discovery manager/finder implementations, and address listers such as the connection service.

Risks: Unexported fields in `CacheEntry` mean external packages can see addresses but not reconstruct fully valid cache entries.

Test signals: Interface conformance is exercised by manager, local, global, and generated mocks.
