# sources/storage-engines/rocksdb/utilities/trie_index/trie_index_factory.cc

## Purpose

Implements the RocksDB trie UDI factory, builder, reader, and iterator declared in `trie_index_factory.h`. The implementation converts block separator keys into a serialized LOUDS trie, stores block handles and sequence-number side-table metadata, deserializes that trie on read, and adapts `LoudsTrieIterator` to the `UserDefinedIndexIterator` contract.

## Important APIs and functions

`TrieIndexBuilder::AddIndexEntry` is called at every data block boundary. It computes a user-key separator with the comparator, detects same-user-key or duplicate-separator boundaries, chooses a packed tag for seqno correction, buffers `(separator_key, tag, handle)`, and returns the separator to RocksDB. `OnKeyAdded` is intentionally a no-op because the trie is built from block separators, not every data key. `Finish` emits the serialized trie by de-duplicating consecutive equal separators into one trie leaf plus overflow blocks.

`TrieIndexBuilder::EstimatedSize` returns an approximate serialized size from accumulated separator bytes and entry count. `TrieIndexIterator` implements `Prepare`, `SeekToFirstAndGetResult`, `SeekToLastAndGetResult`, `SeekAndGetResult`, `NextAndGetResult`, `PrevAndGetResult`, and `value`. `TrieIndexReader::InitFromSlice`, `NewIterator`, and `ApproximateMemoryUsage` wrap the deserialized `LoudsTrie`. `TrieIndexFactory::NewBuilder` and `NewReader` validate the comparator and construct the concrete builder/reader.

## Control flow

Builder flow is deferred: `AddIndexEntry` only buffers entries, and `Finish` makes the all-or-nothing serialization decision. Seqno encoding is effectively always enabled once at least one entry exists. During `Finish`, consecutive entries with identical separator keys form a run. The first entry becomes the trie leaf via `AddKeyWithSeqno`; later entries become overflow blocks via `AddOverflowBlock`. An empty builder still calls `trie_builder_.Finish()` so readers receive a parseable empty trie rather than an empty slice.

Seek flow uses user-key trie search first, then optional seqno correction. `SeekAndGetResult` advances scan option state past exhausted scan ranges, seeks the LOUDS trie by target user key, reconstructs the current separator into scratch storage, and if seqno encoding is present compares `context.target_tag` with the leaf and overflow seqnos to select the correct block in a same-key run. Exhausting the trie returns `IterBoundCheck::kUnknown` rather than `kOutOfBound` so higher-level level iteration does not stop scanning other SSTs prematurely.

Forward and reverse iteration first consume overflow runs when possible. `NextAndGetResult` increments `overflow_run_index_` inside a run before moving to the next trie leaf; `PrevAndGetResult` decrements inside the run before moving to the previous leaf. `value()` returns the primary trie leaf handle for run index 0 and the side-table overflow handle otherwise. Bounds are checked conservatively against a reference key, not the current separator, because trie keys are block upper bounds.

## State and persistence behavior

Persistent state is the serialized LOUDS trie returned by `LoudsTrieBuilder::GetSerializedData()`. It includes trie structure, block handles, a flag for seqno encoding, per-leaf seqnos, block counts, overflow bases, and overflow handles/seqnos owned by `LoudsTrie`. Runtime builder state includes the comparator, buffered entries, a finished guard, a sticky seqno flag, and a running separator-byte total. Runtime iterator state includes scan options, current scan index, scratch strings for current and previous separator keys, and overflow-run indexes.

The reader keeps zero-copy references into the serialized index block and reports memory as raw data size plus `LoudsTrie` auxiliary lookup tables. Because the data slice must remain valid for the reader lifetime, the implementation relies on RocksDB table/block cache lifetime rules.

## Dependencies and integration points

The implementation uses RocksDB's `Comparator`, `Status`, `Slice`, `UserDefinedIndex*` interfaces, `IndexEntryContext::last_key_tag`, `BlockHandle`, `PackSequenceAndType`, and `BytewiseComparator`. It depends on `utilities/trie_index/louds_trie.h` for builder, reader, iterator, block handle, seqno side-table, and overflow metadata. It integrates with block-based table building through `UserDefinedIndexFactory::NewBuilder` and with table reads through `NewReader`.

## Risks and edge cases

The factory only supports bytewise comparator ordering; non-bytewise comparators are rejected because the trie traverses byte lexicographic order. Separator correctness is delicate: the last block deliberately uses the actual last key, not a shortened successor, to avoid widening the indexed key range. Duplicate separators from either same user keys or failed shortening must not receive `kMaxSequenceNumber` sentinel behavior that would break overflow selection. Bound checking must stay conservative or level iteration can terminate too early. The unconditional seqno side-table costs extra bytes per leaf but simplifies last-block and same-key correctness.

## Test signals

Coverage is supplied by `trie_index_db_test.cc` and lower-level trie/SST tests. Relevant signals include same-user-key snapshot reads, duplicate separator reproductions, reverse iteration through overflow runs, last-block separator tests, primary/secondary migration tests, bounds tests, mixed UDI/non-UDI SST fallback, and `EstimatedSizeNonZero` table property checks.
