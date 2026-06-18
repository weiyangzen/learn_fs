<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb.go

Purpose: top-level Go binding setup: API version selection, network lifecycle, database opening helpers, key types, printable byte formatting, and panic-to-error conversion.

Important APIs: `APIVersion`, `MustAPIVersion`, `IsAPIVersionSelected`, `GetAPIVersion`, network options, deprecated `StartNetwork`/`StopNetwork`, `OpenDefault`, `OpenDatabase`, `OpenWithConnectionString`, deprecated `Open`, `CreateCluster`, `KeyConvertible`, `Key`, `Printable`, and internal `executeWithRunningNetworkThread`.

Control flow: `APIVersion` validates once under `networkMutex` and calls `fdb_select_api_version_impl`. Database creation checks API selection, starts the FDB network thread lazily via `executeWithRunningNetworkThread`, calls C creation APIs, caches `OpenDatabase` handles by cluster file, and wraps C pointers in `Database`.

State and persistence: package globals track selected API version, network started/stopped state, network waitgroup, and cached open databases. Database handles own C resources; `Close` in `database.go` removes cached entries.

Dependencies and integration: cgo against `fdb_c.h`; integrates with `Database`, `Cluster`, generated error sentinels, and C network lifecycle.

Risks: API version is process-global and irreversible. Network stop is terminal. `openDatabases.Load` then create/store is not singleflight, so concurrent opens for the same new cluster file may create duplicate handles before last store wins. `panicToError` catches only concrete `Error`. C library/header version mismatch is handled but still operationally sensitive.

Test signals: `fdb_test.go` covers examples, key formatting, default open, close/cache behavior, connection string path, and some network-dependent operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb.go -->
