# sources/storage-engines/rocksdb/util/dirty_tracked.h

Purpose: template wrapper that tracks whether an owned value has been mutated so expensive `Reset()` calls can be skipped when clean.

Important type/API: `DirtyTracked<T>` forwards constructor args to `T`, exposes const read access through `operator->` and `operator*`, exposes mutable access through `mut()` which marks dirty, and `Reset()` calls `value_.Reset()` only when dirty.

Control flow: reads never affect dirty state. Mutations must go through `mut()`. `Reset()` short-circuits unless `dirty_` is true, then clears the flag after resetting the value.

State and persistence: stores `T value_` and `bool dirty_`; no persistence. Dirty state is an optimization hint inside the owning object.

Dependencies and integration: includes `<utility>` and RocksDB namespace. Intended for hot paths where rarely populated helper objects would otherwise allocate or clear unnecessarily.

Risks: correctness depends on all mutations using `mut()`. The wrapper is explicitly not thread-safe. `T` must provide `void Reset()`.

Test signals: no direct test in this subset.
