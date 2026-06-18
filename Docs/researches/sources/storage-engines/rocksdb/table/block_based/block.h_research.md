# sources/storage-engines/rocksdb/table/block_based/block.h

## Purpose

`block.h` declares the in-memory representation and iterator interfaces for parsed RocksDB block-based table blocks. It covers data blocks, metadata blocks, index blocks, read-amplification tracking, and per-key/value checksum protection. The header establishes the contracts that `block.cc`, block-based table readers, cache code, and table-building replay paths rely on when navigating uncompressed key/value blocks.

## Important APIs, types, and functions

- `BlockReadAmpBitmap` maps byte ranges in a block to a coarser bitmap and records `READ_AMP_TOTAL_READ_BYTES` and `READ_AMP_ESTIMATE_USEFUL_BYTES`. It uses atomic bitmap words so concurrent iterators can mark reads safely.
- `Block` owns or references `BlockContents`, parses block footer/restart metadata, creates `DataBlockIter`, `IndexBlockIter`, and `MetaBlockIter`, exposes content and memory accounting, and initializes per-KV checksum protection.
- `BlockIter<TValue>` is the shared iterator base for block entries. It final-overrides movement APIs so subclasses implement only `Seek*Impl`, `NextImpl`, and `PrevImpl`; the base then runs `UpdateKey()` consistently after every movement.
- `DataBlockIter` iterates internal-key data blocks with `Slice` values. It supports read-amp marking, hash-index point lookup through `SeekForGet`, separated-KV storage, and reverse-iteration caching.
- `MetaBlockIter` iterates metadata blocks with bytewise user keys, no sequence numbers, and no read-amp accounting. It is used for properties and metaindex-like blocks.
- `IndexBlockIter` iterates index entries with `IndexValue` values. It supports user-key or internal-key index keys, full or delta-encoded values, optional first internal key, prefix indexing, binary or interpolation restart search, and global seqno rewriting for decoded first keys.
- `Block::GenerateKVChecksum` is the local helper for encoding a protected key/value checksum into the checksum side array.

## Control flow and contracts

`Block` is constructed from `BlockContents` and later manufactures iterators. Iterator creation takes comparator, global seqno, pinning, timestamp persistence, index-value shape, prefix-index, and search-mode options. The returned iterators are either initialized over the block or invalidated with OK/corruption status for empty or malformed blocks.

`BlockIter` enforces a two-phase movement model. Subclasses do raw positioning and parsing in protected `Impl` functions. The public `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, and `Prev` methods then call `UpdateKey()`, which prepares the key visible through `key()`. This is important because a block might store user keys, internal keys, stripped timestamps, or zero seqnos that need to be presented differently to callers.

The base iterator stores offsets rather than owning entries. `current_` points at the current entry offset, `entry_` spans the current encoded entry, `value_` points at the current value, `raw_key_` stores the parsed block key, and `key_buf_` is used only when exposed key bytes must be synthesized. Restart metadata is used for seek and reverse iteration. `GetKeysEndOffset()` abstracts whether entries end at the restart array or at a separated values section.

Checksum protection is configured by passing `protection_bytes_per_key`, `kv_checksum`, and `block_restart_interval` to `InitializeBase`. Subclasses must keep `cur_entry_idx_` accurate because the base uses it to locate the checksum for the current parsed entry in `UpdateKey()`.

## State and persistence behavior

`Block` state mirrors persistent block layout: `restart_offset_`, `num_restarts_`, `is_uniform_`, `data_block_hash_index_`, and `values_section_` are derived from encoded bytes. `block_restart_interval_` can come from table properties or be computed by scanning. `kv_checksum_` is an in-memory protection side array, not part of the block payload.

`BlockReadAmpBitmap` is transient instrumentation state associated with the block. It stores a randomized byte-to-bit alignment so the read amplification estimate avoids consistent boundary bias, and it can update its statistics pointer if the DB replaces the statistics object while the block remains cached.

Iterator pinning state is explicit. `block_contents_pinned_` says block memory outlives cleanup transfer, while `key_pinned_` says the current exposed key points directly into stable memory. Values are pinned whenever block contents are pinned.

## Dependencies and integration points

The header integrates with `InternalIteratorBase`, `PinnedIteratorsManager`, `Cache::Handle`, `Comparator`, `InternalKeyComparator`, `IndexValue`, `BlockContents`, `BlockPrefixIndex`, `DataBlockHashIndex`, table options, statistics, checksum protection, and timestamp-aware key helpers. It is a central dependency for block-based table reading and for builder-side buffered-block replay when compression dictionaries are trained.

The index iterator contract is coupled to `IndexBuilder` serialization choices: `have_first_key`, `key_includes_seq`, `value_is_full`, and restart interval must match between writing, reading, and checksum construction. Data-block iterator hash lookup is coupled to the `DataBlockHashIndex` built by the block builder. Meta-block iteration assumes bytewise keys and restart interval one for metaindex blocks.

## Risks and edge cases

- `BlockIter` relies on subclasses updating `cur_entry_idx_`, `entry_`, `raw_key_`, `value_`, and `restart_index_` consistently. A movement bug can surface as wrong checksum lookup, bad pinning state, or invalid seek results.
- The base destructor and `Invalidate` assert that pinned iterators are not destroyed while pinning is enabled. Mismanaged cleanup transfer can cause debug failures or dangling slices.
- `BlockReadAmpBitmap::Mark` only records useful bytes when the first bit in a range was previously clear, so very coarse `bytes_per_bit` or unusual access patterns can undercount repeated range utility.
- `IndexBlockIter` has multiple optional encodings active at once: delta-encoded values, first keys, global seqno rewriting, timestamp padding, and separated-KV. Reader and writer options must remain synchronized.
- The raw comparator passed into iterators must be the unwrapped user comparator. Passing a wrapped comparator would break internal/user-key comparison assumptions.
- Metadata blocks intentionally avoid strict assertions on malformed content in some contexts, while data and index blocks are more strict. Tests need to account for those different tolerance levels.

## Test signals

Test hooks and debug-only methods include corruption callbacks in movement functions, `TEST_CurrentEntrySize`, `TEST_GetKVChecksum`, `SetPinnedItersMgr`, and read-amp randomization sync points. Useful tests should cover pinning transfer, cache-handle reference behavior, checksum initialization and verification, timestamp persistence toggles, global seqno rewriting, data hash index lookup, prefix-index seeks, interpolation search selection, separated-KV boundaries, and reverse iteration cache behavior.
