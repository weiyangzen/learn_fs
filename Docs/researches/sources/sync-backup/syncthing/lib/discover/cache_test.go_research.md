## sources/sync-backup/syncthing/lib/discover/cache_test.go

Purpose: Tests discovery manager cache aggregation, address uniqueness/sorting, and lookup concurrency behavior.

Important APIs/types/functions: `setupCache`, `TestCacheUnique`, `TestCacheSlowLookup`, `fakeDiscovery`, and `slowDiscovery`.

Control flow: Tests create a manager with local/global announcement disabled, manually add fake finders under lock, call `Lookup`, and compare sorted unique results. Slow lookup test starts a lookup that holds the read lock path and asserts `ChildErrors` returns quickly.

State and persistence: In-memory fake manager and fake finders only.

Dependencies and integration points: Uses config wrapper, events noop logger, registry, and manager internals.

Risks: Tests call unexported `addLocked`, so they are coupled to manager internals.

Test signals: Good coverage for multi-finder deduplication and avoiding lock contention between lookup and child error reporting.
