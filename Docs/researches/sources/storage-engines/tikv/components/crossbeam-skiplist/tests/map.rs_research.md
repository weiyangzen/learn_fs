# sources/storage-engines/tikv/components/crossbeam-skiplist/tests/map.rs

Purpose: This suite validates the public `SkipMap` API and its guard-hiding entry/iterator wrappers. It mirrors much of the base behavior while adding tests for `compare_insert` and wrapper-specific memory release regressions.

Important APIs and tests: It uses `SkipMap`, `Arc`, `Barrier`, `crossbeam_utils::thread`, `Bound`, and collection construction from iterators. Notable tests include `compare_and_insert`, `compare_insert_with_absent_key`, `concurrent_insert`, `concurrent_compare_and_insert`, `concurrent_remove`, `next_memory_leak`, `next_back_memory_leak`, `range_next_memory_leak`, `ordered_iter`, `ordered_range`, `iter_range2`, and `concurrent_insert_get_same_key`.

Control flow: Tests perform deterministic insert/remove sequences and collect ordered keys. Concurrency regressions run repeated two-thread same-key races or many compare-insert writers. Iterator tests interleave mutation with traversal and mix `next`/`next_back` calls to verify cursors terminate and release references correctly.

State and persistence behavior: All state is in-memory. Tests inspect public length, emptiness, entry removal flags, values after replacement, and iterator output.

Dependencies and integration points: The suite is a contract for users of `SkipMap` and indirectly exercises `base::SkipList`, `Entry::Drop`, `Iter::Drop`, and `Range::Drop`.

Risks: It cannot prove all lock-free interleavings, but it captures prior Crossbeam issues around duplicate same-key insertion/removal, range counting, and same-key insert/get visibility.

Test signals: Exact expected values and sorted sequences are the main signals; concurrency tests signal panic-free execution, max-value compare-insert convergence, and persistent `get` success while another thread repeatedly inserts the same key.
