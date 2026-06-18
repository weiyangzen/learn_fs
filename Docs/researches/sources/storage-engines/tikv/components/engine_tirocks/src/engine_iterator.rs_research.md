<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/engine_iterator.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/engine_iterator.rs

## Purpose
`engine_iterator.rs` adapts tirocks iterators to `engine_traits::Iterator` and converts TiKV iteration options to tirocks read options, including range bounds, prefix behavior, key-only reads, and MVCC timestamp table filtering.

## Important APIs, Types, and Functions
`RocksIterator<'a, D>` wraps `tirocks::Iterator<'a, D>` and exposes `from_raw` plus `sequence`. Its trait implementation forwards seek/next/prev/key/value/valid.

`TsFilter` implements tirocks `TableFilter`, reading `tikv.max_ts` and `tikv.min_ts` user properties to skip tables outside hint timestamp bounds. `to_tirocks_opt(IterOptions)` builds `ReadOptions` from engine-trait options. Type aliases define engine and snapshot iterator shapes.

## Control Flow
Seek methods call tirocks seek functions then `valid`. `valid` returns true when the iterator is valid, otherwise calls `check` to surface stored iterator errors. `next`/`prev` check validity first unless `nortcheck` is enabled. `key`/`value` assert validity in checked builds.

Option conversion sets fill-cache, max skippable internal keys, key-only, total-order or prefix-same-as-start behavior, disables auto-prefix and adaptive readahead for now, installs `TsFilter` when timestamp hints exist, and applies lower/upper bounds from `IterOptions::build_bounds`.

## State and Persistence Behavior
Iterators are read-only but can hold RocksDB resources and snapshots alive. `TsFilter` affects which SST tables are read during iteration but does not change persisted data.

## Dependencies and Integration Points
It depends on tirocks iterator/read option/table-filter APIs, TiKV number codec for decoding table properties, and `engine_traits::IterOptions`. Timestamp filter property names must match MVCC property collectors in this crate and `engine_rocks`.

## Risks and Edge Cases
Hard-coded `tikv.max_ts`/`tikv.min_ts` names are called out as TODOs. If properties are absent or undecodable, tables are not filtered, preserving correctness at cost of extra IO. `key`/`value` can panic if called on invalid iterators in checked builds. Total-order seek disables auto-prefix mode with a TODO rather than fully enabling desired behavior.

## Test Signals
Engine scan tests exercise basic iteration and snapshot isolation. More focused tests should cover lower/upper bounds, reverse iteration, key-only mode, prefix modes, timestamp table filtering with present/missing/corrupt MVCC properties, and iterator error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/engine_iterator.rs -->
