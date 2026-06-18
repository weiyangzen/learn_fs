# sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound_set.cpp

Purpose: Implements paired lower/upper cursor bounds, including prefix-range construction.

Important APIs/types/functions: `bound_set(bound lower, bound upper)` stores a pair. `bound_set(const std::string &key)` creates an inclusive lower bound at `key` and an exclusive upper bound by incrementing the last byte of the key copy. `apply` applies both bounds to a cursor. Getters return references to lower and upper bounds.

Control flow: prefix constructor derives the upper bound eagerly; `apply` sets the key for each bound and calls `cursor->bound` twice with fatal checking.

State and persistence: keeps two in-memory `bound` objects and mutates cursor-bound state when applied.

Dependencies/integration: uses `bound`, `scoped_cursor`, and `test_util`; provides a convenience layer for prefix scans in tests.

Risks and test signals: prefix construction assumes a non-empty key and simple byte increment; overflow or collation-specific ordering can make the range wrong. WT cursor-bound errors are test failures.
