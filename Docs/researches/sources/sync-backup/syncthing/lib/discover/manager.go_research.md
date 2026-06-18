## sources/sync-backup/syncthing/lib/discover/manager.go

Purpose: Aggregates multiple discovery mechanisms, manages their lifecycle from configuration, caches lookup results, and exposes combined cache/error state.

Important APIs/types/functions: Public `Manager` interface; `manager` struct; `NewManager`; `serve`; `addLocked`; `removeLocked`; `Lookup`; `ChildErrors`; `Cache`; and `CommitConfiguration`.

Control flow: Manager subscribes to config in `serve` and reconciles finders in `CommitConfiguration`. Global servers are added with five-minute positive and one-minute negative caches; local IPv4/IPv6 discovery is added without manager-level caching. `Lookup` scans finders under read lock, uses valid positive/negative cache entries, performs finder lookups when needed, caches success/failure, deduplicates and sorts addresses, and returns nil error. `Cache` merges positive manager cache entries with child finder caches.

State and persistence: Holds a supervised map of finder identities to `cachedFinder` entries under RW mutex. No durable state.

Dependencies and integration points: Integrates config options, global/local discovery constructors, event logger, registry, address lister, TLS cert, and suture supervisor.

Risks: `Lookup` holds `m.mut.RLock` while calling finder `Lookup`, so config updates requiring write lock can wait on slow discovery; tests only check `ChildErrors` read path. Negative-cache errors are swallowed from the public return, so callers see empty addresses/nil error.

Test signals: Cache tests cover aggregation and ChildErrors during slow lookups; global/local tests cover child implementations.
