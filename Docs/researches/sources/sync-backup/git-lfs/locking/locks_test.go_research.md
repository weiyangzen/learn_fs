# sources/sync-backup/git-lfs/locking/locks_test.go

Purpose: verifies the locking client's remote search and cache refresh behavior against local HTTP test servers.

Important APIs/types/functions: `LocksById` provides deterministic sorting. `TestRemoteLocksWithCache`, `TestRefreshCache`, and `TestSearchLocksVerifiableWithCache` exercise `NewClient`, `SetupFileCache`, `prepareCacheDirectory`, `SearchLocks`, and `SearchLocksVerifiable`.

Control flow: each test creates a temp cache and `httptest.Server`, configures an `lfsapi.Client` with `lfs.url`, sets `RemoteRef`, then asserts when network calls happen and when cache files appear. Remote search with filters or limits must not create cache files; unlimited remote search must create them. Verifiable search walks two cursor pages before caching.

State/persistence behavior: tests inspect cache-file existence and fixed encoded sizes, then read the cached data back without incrementing the remote query counter. `TestRefreshCache` also confirms verifiable search repopulates the local in-memory lock cache.

Dependencies/integration: uses `lfshttp.NewContext`, `config.New`, `git.Ref`, JSON encoding of lock response structs, and testify assertions.

Risks: fixed byte-size assertions are sensitive to JSON formatting and struct shape. Tests sort only after collecting data, so ordering is intentionally not part of the remote contract.

Test signals: failures indicate regressions in cache gating, pagination, ref-scoped cache paths, local cache refresh, or cached verifiable result decoding.
