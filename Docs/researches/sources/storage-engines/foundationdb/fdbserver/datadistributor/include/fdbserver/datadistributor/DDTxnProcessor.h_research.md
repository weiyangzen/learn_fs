# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDTxnProcessor.h

Purpose: defines the transaction/data-plane abstraction used by DD, plus real and mock implementations. It isolates DD control logic from direct `Database`/NativeAPI calls and makes mock testing possible.

Important APIs and types: `IDDTxnProcessor` declares `context()`, `isMocked()`, source-server lookup, source interface lookup, `waitForAllDataRemoved()`, server-list reads, initial DD load, move-keys lock management, configuration reads, replica-key updates, DD enabled checks, lock polling, failed-server key removal, storage-server removal, `moveKeys()`, storage metric wait/split, read-hot ranges, health metrics, ignore-key reads, team-info print signal, worker listing, and storage stats. `DDTxnProcessor` implements the real database path. `DDMockTxnProcessor` implements mock state backed by `MockGlobalState`.

Control flow: real implementation delegates to NativeAPI and system-key operations, including move-key start/finish helpers. Mock implementation returns immediately where transaction atomicity is assumed, uses in-memory shard/server state, and exposes `setupMockGlobalState()` for tests. The interface lets DD components request behavior without knowing whether they run against a cluster or mock.

State and persistence: `DDTxnProcessor` stores a `Database cx` and performs durable reads/writes externally. `DDMockTxnProcessor` stores a shared `MockGlobalState` and mutates transient in-memory maps/server state. The interface makes persistence semantics explicit by forcing all database-affecting operations through this layer.

Dependencies and integration: includes knobs, move keys, `MockGlobalState`, `InitialDataDistribution`, `DDShardInfo`, storage metrics, health metrics, and data movement structures. It is referenced by shard tracker, team collection, TC metrics polling, physical shard collection, and mock DD.

Risks: default interface methods returning `Void`, `Never`, or empty vectors must be overridden where production behavior is required. Mock `context()` is unreachable, so code paths that leak direct database access break testability. Real and mock move semantics must stay aligned or mock DD tests can pass while production behavior differs.

Test signals: tests should assert DD components use this abstraction instead of direct `Database` calls, compare real/mock source-server semantics, cover failed-server removal, initial-data reconstruction, storage metrics split/wait behavior, and DD-enabled lock polling.
