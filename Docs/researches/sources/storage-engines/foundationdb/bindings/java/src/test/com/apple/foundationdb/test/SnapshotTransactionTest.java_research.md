# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SnapshotTransactionTest.java

Purpose: integration tests for snapshot read conflict behavior and snapshot transaction identity semantics.

Important APIs and flow: `addUUIDConflicts` adds random read/write conflict keys so commits participate in conflict resolution. `snapshotReadShouldNotConflict` verifies snapshot key/range reads do not conflict while normal reads do. `snapshotShouldNotAddConflictRange` checks `addReadConflictRangeIfNotSnapshot` and `addReadConflictKeyIfNotSnapshot` return false on snapshots and true on normal transactions. `snapshotOnSnapshot` checks `isSnapshot`, pointer inequality for `tr.snapshot()`, and idempotence of snapshot-on-snapshot.

State and persistence: uses a `Subspace` under `("test","conflict_ranges")` only for conflict keys; no intentional data writes except conflict ranges. Risks include reliance on conflict code 1020, timeout sensitivity, and careful transaction ordering. Signal is strong because failures throw runtime exceptions after validating exception causes.
