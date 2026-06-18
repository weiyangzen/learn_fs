# sources/storage-engines/tikv/components/engine_traits/src/iterable.rs

Purpose: Defines TiKV's generic iterator model for engines, snapshots, and SST readers.

Important APIs and control flow: `Iterator` supports seek, seek-for-prev, first/last, next/prev, key/value, and validity checks. `RefIterable` creates borrowing iterators for SST-style readers. `IterMetricsCollector` and `MetricsExt` expose skipped-key and block-read metrics. `Iterable` creates owned iterators and provides `scan` and `seek` helpers; `scan_impl` seeks to the start key and repeatedly invokes a callback until it returns false or the iterator ends. `iter_option` builds bounded iterator options.

State, persistence, and dependencies: Iterators hold backend cursor/snapshot state over persistent key-value data. Helpers do not persist state.

Integration points, risks, and test signals: Used by all range scans, snapshots, SST readers, and tests. Risks include invalid iterator panics, bounds misuse, inconsistent engine-vs-snapshot views, callback early termination, and metric defaults hiding backend reads. Shared iterator tests exhaust empty, forward, reverse, seek, seek-for-prev, direction changes, and miss semantics.
