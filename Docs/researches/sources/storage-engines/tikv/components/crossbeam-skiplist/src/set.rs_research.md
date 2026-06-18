# sources/storage-engines/tikv/components/crossbeam-skiplist/src/set.rs

Purpose: `set.rs` implements `SkipSet<T>` as a thin ordered set wrapper around `SkipMap<T, ()>`. It preserves the concurrent ordered behavior while exposing values as set entries rather than map keys.

Important APIs and types: Public types are `SkipSet`, set `Entry`, `IntoIter`, `Iter`, and `Range`. Methods mirror `SkipMap`: `new`, `is_empty`, `len`, `front`, `back`, `contains`, `get`, `lower_bound`, `upper_bound`, `get_or_insert`, `iter`, `range`, `insert`, `remove`, `pop_front`, `pop_back`, and `clear`. `Entry` dereferences to `T` and exposes `value`, navigation, `is_removed`, and `remove`.

Control flow: All operations delegate to `SkipMap<T, ()>`, converting map entries into set entries. `IntoIter` drops the unit value and yields only keys. Range and iterator behavior is inherited from the map layer.

State and persistence behavior: State is in-memory and stored in the underlying skip map. Entries hold map references, so removed values remain alive while entries exist.

Dependencies and integration points: It depends on `map.rs`, standard borrowing/range traits, `Deref`, and standard collection traits. It is reexported by `lib.rs` with the `std` feature.

Risks: Risks largely match `SkipMap`: approximate `len` under concurrency, immutable-only access, and logical races across multiple calls. Because the set is a map-to-unit adapter, correctness depends on key-only semantics being preserved by all map operations.

Test signals: `tests/set.rs` validates set insertion/removal, duplicate length behavior, entry navigation/reposition after removal and reinsertion, bounds, range combinations, iterator ordering, clear, into-iter output, and same-key concurrent insert/get.
