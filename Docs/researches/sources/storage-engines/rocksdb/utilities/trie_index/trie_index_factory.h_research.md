# sources/storage-engines/rocksdb/utilities/trie_index/trie_index_factory.h

## Purpose

Declares the public experimental trie UDI components for RocksDB block-based tables. The header exposes `TrieIndexFactory`, the builder used during SST creation, the reader used for deserialized UDI blocks, and the iterator adapter used by table reads. It documents the intended use: set `BlockBasedTableOptions::user_defined_index_factory` when writing, and use `ReadOptions::table_index_factory` in secondary mode when reading.

## Important APIs and types

`TrieIndexBuilder final : UserDefinedIndexBuilder` owns a `LoudsTrieBuilder`, comparator pointer, finished flag, seqno-encoding flag, buffered separator entries, and a separator byte counter. Its API is `AddIndexEntry`, `OnKeyAdded`, `Finish`, and `EstimatedSize`. `BufferedEntry` stores the user-key separator, packed tag, and `TrieBlockHandle` for each block-boundary entry.

`TrieIndexIterator final : UserDefinedIndexIterator` adapts `LoudsTrieIterator` to RocksDB's UDI iteration contract. It exposes `Prepare`, seek-to-first/last, seek, next, prev, and `value`. It stores scan options, current scan index, prepared state, current and previous key scratch strings, trie pointer, comparator pointer, and overflow-run state (`overflow_run_index_`, `overflow_run_size_`, `overflow_base_idx_`). Inline helpers reset or initialize overflow state and copy trie keys into the UDI result.

`TrieIndexReader : UserDefinedIndexReader` owns a `LoudsTrie` plus comparator and raw data size. It initializes from a serialized slice, creates iterators, and reports approximate memory usage. `TrieIndexFactory : UserDefinedIndexFactory` names the customizable `"trie_index"`, aborts deprecated builder/reader APIs, and implements comparator-aware `NewBuilder` and `NewReader` overloads accepting `UserDefinedIndexOption`.

## Control flow contract

The builder contract follows RocksDB SST construction order: `OnKeyAdded` may be called for every key, `AddIndexEntry` is called for each data block boundary, then `Finish` serializes the index. The header makes clear that actual trie construction is deferred until `Finish`, allowing the implementation to make a global seqno side-table decision after all separator entries are known.

The iterator contract is scan-oriented. `Prepare` receives one or more `ScanOptions` ranges. Seeking positions the trie and sets result keys; next/prev advance either through overflow blocks for same-key runs or through trie leaves. `value()` must return the handle matching the logical current block, including overflow blocks, rather than blindly returning the trie leaf handle.

## State and persistence behavior

The header separates persistent trie contents from transient adapters. Persistent contents are produced by `LoudsTrieBuilder` and later loaded into `LoudsTrie`. Transient build state is the buffered list of separators and tags. Transient read state is held per iterator, so multiple iterators can independently maintain bounds, scratch keys, and overflow positions over the same reader-owned trie.

Seqno handling is a central state contract: the comments state that seqno encoding is always enabled after entries are added, with an 8-byte per-leaf overhead. Tags distinguish same-user-key boundaries, last-block separators, and ordinary non-boundary separators using real packed tags or the 0 sentinel.

## Dependencies and integration points

The header depends on `rocksdb/user_defined_index.h`, `rocksdb/comparator.h`, `rocksdb/types.h`, and `utilities/trie_index/louds_trie.h`. It is included by DB tests, the factory implementation, and block-table code that instantiates UDI builders/readers through the `UserDefinedIndexFactory` interface. It also participates in RocksDB's `Customizable` naming through `Name()` and `kClassName()`.

## Risks and edge cases

Deprecated base-class APIs abort unconditionally, so callers must use the `UserDefinedIndexOption` overloads. The comparator pointer is non-owning and must remain valid under RocksDB's options lifetime rules. Reader slices must remain alive for the reader because `LoudsTrie` uses serialized data directly. Iterator scratch strings back returned `Slice` keys, so result key lifetimes are tied to the iterator and overwritten on movement. Overflow state must be reset or initialized correctly on every movement to avoid returning the wrong block handle.

## Test signals

The DB test suite validates this header's contract through builder creation, reader creation, iterator movement, primary/secondary routing, seqno overflow handling, and estimated size. The implementation's bytewise-comparator restriction and deprecated API abort behavior should be considered API compatibility signals when integrating with other comparator or Customizable paths.
