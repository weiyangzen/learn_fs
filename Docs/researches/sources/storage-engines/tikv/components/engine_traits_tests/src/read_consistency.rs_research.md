# sources/storage-engines/tikv/components/engine_traits_tests/src/read_consistency.rs

Purpose: Tests snapshot and iterator read consistency while later writes and deletes occur.

Important APIs and control flow: `snapshot_with_writes` captures a snapshot after writing `a`, then verifies it does not see later key `b` and still sees deleted key `a`. `iterator_with_writes` creates an iterator after keys `a` and `c`, then verifies later inserted keys are not seen and later deletes do not alter the iterator's view. The helper is run for engine-created iterators and snapshot-created iterators.

State, persistence, and dependencies: Temporary engine state mutates after snapshots/iterators are created; expected view state is pinned by the iterator/snapshot.

Integration points, risks, and test signals: Catches implementations whose engine iterators are live cursors rather than snapshot-consistent views. Risks include backend snapshot isolation gaps and iterator invalidation after writes.
