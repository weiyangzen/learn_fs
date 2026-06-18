# sources/storage-engines/leveldb/issues/issue200_test.cc

Purpose: regression test for iterator direction-switch behavior after a mutation outside the iterator's snapshot.

Important APIs and functions: test `Issue200.Test`.

Control flow: opens a DB, writes keys `1` through `5`, creates an iterator, writes key `25`, then seeks to `5`, moves backward to `3`, and forward to `5`, asserting the new `25` does not disturb the iterator sequence.

State and persistence behavior: relies on iterator creation capturing a stable view independent of later writes.

Dependencies and integration: uses public `DB`, `Iterator`, `ReadOptions`, `WriteOptions`, and test utilities. It targets DB iterator merging and direction-change code outside this subset.

Risks and edge cases: narrow regression, not a broad iterator fuzz test. It assumes bytewise key order where `"25"` sorts between `"2"` and `"3"` lexicographically.

Test signals: precise signal for a historical duplicate/unexpected-yield bug on `Prev` to `Next` transition.
