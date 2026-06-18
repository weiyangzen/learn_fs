# sources/storage-engines/leveldb/issues/issue178_test.cc

Purpose: regression test for issue 178, where manual compaction could cause deleted data to reappear.

Important APIs and functions: helpers `Key1`, `Key2`, constant `kNumKeys`, and test `Issue178.Test`.

Control flow: creates a DB with compression disabled, bulk writes a first key range and a second related key range, deletes the second range, manually compacts only the first range, then iterates the DB and expects exactly the first-range key count.

State and persistence behavior: forces large table/level state and tombstones, then validates compaction preserves delete semantics. Disabling compression stabilizes file layout enough to hit the target scenario.

Dependencies and integration: uses public `DB`, `WriteBatch`, `CompactRange`, iterators, and `DestroyDB`. It is tied to compaction boundary and obsolete-entry logic in `VersionSet`/`DBImpl`.

Risks and edge cases: large `kNumKeys` makes it a heavier regression. The test counts keys rather than checking every key's value/deletion state.

Test signals: high-value regression for compaction not resurrecting deleted range data.
