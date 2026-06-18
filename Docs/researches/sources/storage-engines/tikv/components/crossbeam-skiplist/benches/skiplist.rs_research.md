# sources/storage-engines/tikv/components/crossbeam-skiplist/benches/skiplist.rs

Purpose: benchmark suite for the low-level `SkipList` API using Crossbeam epoch guards.

Important APIs and types: benchmark functions `insert`, `iter`, `rev_iter`, `lookup`, and `insert_remove`; `SkipList`, `crossbeam_epoch::pin`, `epoch::default_collector`, and entry `release`.

Control flow: each operation uses the same deterministic `u64` sequence as baseline benches. Insert creates a new skiplist per iteration and inserts under a pinned guard. Iteration and lookup prepopulate a list and release insertion entries. Remove benchmarks remove and release entries within each iteration.

State and persistence: in-memory skiplist nodes reclaimed by Crossbeam epoch mechanisms; no persistence.

Dependencies and integration: exercises the base skiplist API directly rather than the higher-level `SkipMap`. It is useful for comparing raw skiplist costs to standard maps and for noticing regressions in epoch-protected traversal/removal.

Risks: pinned guards held for a full benchmark can affect reclamation timing and may not mirror production guard scopes. Single-threaded benchmarks do not capture concurrent contention behavior. Uses unstable `test` harness.

Test signals: raw performance signal for insert, forward/reverse iteration, lookup, and insert/remove cycles in the forked skiplist.
