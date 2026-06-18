# sources/storage-engines/tikv/components/crossbeam-skiplist/tests/set.rs

Purpose: This suite validates the public `SkipSet` API as a set-oriented adapter over `SkipMap<T, ()>`. It ensures key-only behavior, ordering, range semantics, entry navigation, and same-key concurrency remain correct.

Important APIs and tests: It uses `SkipSet`, `crossbeam_utils::thread`, `Barrier`, `Bound`, and iterator collection. Test names cover smoke construction, emptiness, insertion, removal, concurrent insert/remove, entry navigation/removal/reposition, length, get, lower/upper bounds, `get_or_insert`, front/back, iterators, ranges, `iter_range2`, `into_iter`, `clear`, and `concurrent_insert_get_same_key`.

Control flow: Tests create fixed integer sets, mutate them, and collect ordered values through `Entry` deref. Range tests exhaust combinations of included/excluded/unbounded bounds. Concurrency tests use repeated two-thread races and a longer same-key insert/get loop.

State and persistence behavior: All state is in-memory. Since entries wrap map entries, removed elements are observable through `is_removed` and remain valid while referenced.

Dependencies and integration points: It tests the set wrapper and indirectly the map/base layers. It is especially useful for checking that map key/value behavior did not leak into the set API.

Risks: The same-key insert/get test uses a fixed loop count and does not explore arbitrary schedules. Like the map suite, it validates behavior but not full lock-free progress guarantees.

Test signals: Sorted value outputs, duplicate insertion preserving length, removed-entry flags, empty/non-empty transitions, exact range vectors, and panic-free concurrent same-key operations provide the primary signals.
