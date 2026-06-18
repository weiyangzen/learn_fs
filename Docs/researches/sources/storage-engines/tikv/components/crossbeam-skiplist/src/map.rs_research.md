# sources/storage-engines/tikv/components/crossbeam-skiplist/src/map.rs

Purpose: `map.rs` exposes the ergonomic, `std`-based `SkipMap<K,V>` API on top of `base::SkipList<K,V>`. It gives users a concurrent ordered map without requiring them to manage epoch guards or `RefEntry` release manually.

Important APIs and types: Public types are `SkipMap`, `Entry`, `IntoIter`, `Iter`, and `Range`. Main methods include `new`, `is_empty`, `len`, `front`, `back`, `contains_key`, `get`, `lower_bound`, `upper_bound`, `get_or_insert`, `get_or_insert_with`, `iter`, `range`, `insert`, `compare_insert`, `remove`, `pop_front`, `pop_back`, and `clear`. `Entry` exposes `key`, `value`, `is_removed`, navigation, cloning, and `remove`.

Control flow: Each operation pins the default epoch collector, calls the corresponding `base::SkipList` method, and converts `RefEntry` into a public `Entry`. `try_pin_loop` retries when a found guarded node cannot be reference-counted because concurrent removal won the race. Iterators and ranges hold `base::RefIter`/`RefRange` state and release cursor references in `Drop`.

State and persistence behavior: The map stores all key/value pairs in its inner skip list. `Entry` uses `ManuallyDrop` so its `Drop` implementation can consume the `RefEntry` and call `release_with_pin`. There is no disk persistence.

Dependencies and integration points: It integrates public Rust collection traits (`Default`, `IntoIterator`, `FromIterator`, `Debug`) with the unsafe base implementation and `crossbeam_epoch::default_collector`.

Risks: Returned entries keep removed nodes alive until dropped. Values are only shared immutably; callers needing mutation must use interior mutability. `get_or_insert_with` may evaluate and discard its closure result if another thread inserts first.

Test signals: `tests/map.rs` covers duplicate insertion, compare-insert semantics, concurrent insert/remove regressions, iterator memory-leak regressions, ordered forward/backward iteration, range bounds, clear, into-iter ordering, panic safety, and concurrent same-key insert/get.
