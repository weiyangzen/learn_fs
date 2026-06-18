# sources/storage-engines/tikv/components/engine_traits_tests/src/snapshot_basic.rs

Purpose: Tests point reads from snapshots for default and named column families.

Important APIs and control flow: Tests write a key, take a snapshot, read existing and missing keys, then mutate the engine and verify the snapshot still returns the old value. CF-specific tests repeat the pattern for `CF_WRITE` on an all-CF engine.

State, persistence, and dependencies: Engine state changes after snapshot creation, but snapshot read state must remain fixed.

Integration points, risks, and test signals: Validates `KvEngine::snapshot`, `Snapshot + Peekable`, and CF-specific snapshot reads. Risks include snapshot views not pinning sequence numbers, named CF handle mistakes, and post-write visibility leaks.
