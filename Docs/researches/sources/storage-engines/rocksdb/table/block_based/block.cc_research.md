# sources/storage-engines/rocksdb/table/block_based/block.cc

## Purpose

`block.cc` implements the parsed block reader and iterator algorithms declared in `block.h`. It decodes uncompressed block-based table blocks produced by `block_builder.cc`, supports data, metadata, and index block iteration, and handles modern block-format features such as data-block hash indexes, separated key/value storage, value-delta-encoded index entries, interpolation search for uniform index blocks, global-sequence-number rewriting, user-defined timestamp padding, read-amplification accounting, and per-key/value checksum verification.

## Important APIs, types, and functions

- `DataBlockIter::SeekImpl`, `SeekForGetImpl`, `SeekForPrevImpl`, `NextImpl`, `PrevImpl`, `SeekToFirstImpl`, and `SeekToLastImpl` implement ordered navigation over internal-key data blocks. `SeekForGetImpl` uses `DataBlockHashIndex` when present, falling back to binary restart search on collisions or unsupported value types.
- `MetaBlockIter` implements the same movement primitives for metadata blocks, using strict entry decoding and bytewise user-key ordering.
- `IndexBlockIter::SeekImpl`, `PrefixSeek`, `BinaryBlockIndexSeek`, `FindRestartPointForSeek`, `DecodeCurrentValue`, and movement methods implement index-block lookup. It supports prefix-index lookup, binary search, interpolation search, delta-encoded block handles, optional first internal key, and global seqno rewriting for first keys.
- `BlockIter<TValue>::ParseNextKey` is the core entry decoder. It advances from `entry_`, decodes shared/non-shared key bytes and value length, rebuilds delta-encoded keys, updates restart index state, and supports separated KV by resolving value slices from the values section.
- `BlockIter<TValue>::BinarySeekRestartPointIndex`, `InterpolationSeekRestartPointIndex`, `GetRestartKey`, and `FindKeyAfterBinarySeek` provide restart-array search plus final linear scan within a restart interval.
- `Block::Block` parses `DataBlockFooter`, initializes restart metadata, strips hash-index suffixes, recognizes separated KV sections, and creates read-amp bitmaps when configured.
- `Block::InitializeDataBlockProtectionInfo`, `InitializeIndexBlockProtectionInfo`, and `InitializeMetaIndexBlockProtectionInfo` precompute per-entry checksums using iterators over the parsed block.
- `Block::NewDataIterator`, `NewIndexIterator`, and `NewMetaIterator` allocate or initialize iterators, validate block size/restart state, and pass checksum, separated-KV, timestamp, prefix-index, and search-mode state into the iterator.

## Control flow

Iterator movement always follows the same high-level contract: subclass `*Impl()` functions position `raw_key_`, `value_`, `entry_`, `current_`, and restart bookkeeping, while the final methods in `BlockIter` call `UpdateKey()` exactly once afterward. `UpdateKey()` then exposes either the raw internal key, raw user key, or a synthesized internal key with `global_seqno_`, and verifies per-KV checksum when enabled.

Forward iteration uses `ParseNextKey`. The function advances `current_` to the end of the previous entry, decodes the entry header, reconstructs the key from shared and non-shared bytes, and sets `value_`. In regular blocks values are inline immediately after key bytes; in separated-KV blocks the first entry in each restart interval encodes a value offset and later entries derive their value slice from the previous value. Corruption is reported if decoding fails, shared-key state is inconsistent, strict bounds checks fail, or separated-KV slices would pass the restart array.

Reverse iteration scans backward to the preceding restart point and then parses forward until the entry before the original position. `DataBlockIter::PrevImpl` adds a cache of parsed previous entries so repeated reverse movement within the same restart interval can avoid reparsing and reassembling delta-encoded keys. Index and meta iterators use the simpler restart-scan approach.

Seek first locates a restart interval and then scans within it. Data and metadata seeks always use binary restart search. Index seeks can use prefix lookup when a `BlockPrefixIndex` is supplied and total-order seek is not requested. Otherwise, index seeks choose binary or interpolation search through `FindRestartPointForSeek`. `kAuto` search resolution happens in `Block::NewIndexIterator`, based on the block uniformity bit and bytewise comparator compatibility.

Point lookup has an additional data-block fast path. `DataBlockIter::SeekForGetImpl` asks `DataBlockHashIndex` for the restart interval for the target user key. Collisions fall back to full seek. Missing entries are treated carefully because the lookup may need to continue in the next data block depending on block-boundary ordering. The optimized path only trusts a limited set of value types; other types fall back to normal seek.

`Block::Block` is the entry point for parsed block construction. It decodes the footer, records `num_restarts_` and `is_uniform_`, validates the data-block index type, initializes `data_block_hash_index_` for binary-and-hash blocks, trims the input view back to the restart array, computes `restart_offset_`, validates separated-KV offsets, and marks malformed blocks by setting the content size to zero. Later iterator construction detects that marker and returns a corruption status, with `GetCorruptionStatus()` re-decoding the footer to preserve a more specific error when possible.

## State and persistence behavior

The code reads persistent block bytes but does not write file data. Persistent layout assumptions include entry delta encoding, restart arrays, data-block footers, optional hash-index payloads, optional separated-KV value sections, and encoded `IndexValue` records. `Block` stores a moved `BlockContents` object and then derives non-owning pointers such as `values_section_` into `contents_.data`.

Iterator state is transient and points into block memory unless key reconstruction, timestamp padding, or global seqno rewriting requires internal buffers. `block_contents_pinned` controls whether returned key/value slices may be treated as pinned by higher layers. The read-amplification bitmap persists for the lifetime of the `Block` and records useful-byte statistics lazily when values are read.

Per-KV protection state is stored in heap memory owned by `Block` as `kv_checksum_`, with `checksum_size_` and `protection_bytes_per_key_` describing the array. The checksum is generated by scanning all entries after block construction and is verified during iterator `UpdateKey()` for the current visible key.

## Dependencies and integration points

This file depends on `DataBlockFooter`, `DataBlockHashIndex`, `BlockPrefixIndex`, `IndexValue`, `BlockHandle` decoding, `InternalKeyComparator`, timestamp helpers, RocksDB statistics/perf context, and block-format coding utilities. It is used by block-based table readers, cache warmers, dictionary-buffer replay in `block_based_table_builder.cc`, meta-block readers, index readers, and tests injecting corruption through sync points.

Important integration contracts include:

- `BlockBuilder` must produce entries whose footer, restart array, hash index, and separated-KV offsets match the parser expectations here.
- `IndexBuilder` and table properties must agree with `have_first_key`, `value_is_full`, `key_includes_seq`, and restart interval settings used when creating index iterators and per-KV checksums.
- Callers using global seqno must only read blocks whose encoded seqnos are zero and whose value types are permitted by the assertions.
- Prefix index seek may return invalid with `NotFound` when the prefix is definitely absent, which upper layers use differently from end-of-block invalidation.

## Risks and edge cases

- Corruption handling relies on carefully preserving the error marker state. Some paths intentionally set `contents_.data.size_ = 0`, after which iterator constructors must avoid dereferencing block internals.
- Per-KV checksum verification is tied to `cur_entry_idx_`. Comments note cases where seeking to the end after scanning might not verify the last parsed key because `UpdateKey()` sees the iterator invalid.
- Interpolation search assumes bytewise comparator semantics and can fall back to binary search after poor guesses. Incorrect use with another comparator would violate ordering assumptions; `NewIndexIterator` guards `kAuto`, but explicit interpolation relies on assertions.
- Separated-KV support changes the meaning of the keys-end offset. Code that accidentally uses `restarts_` instead of `GetKeysEndOffset()` could overrun into values or restart metadata.
- `DataBlockIter::PrevImpl` caches slices and copied key bytes. The distinction between pinned block key data and transient cached buffers is subtle and affects `IsKeyPinned()`.
- Data-block hash lookup is conservative. False positives, collisions, non-point-like value types, and next-block boundary cases all need fallback behavior to preserve correctness.
- Timestamp stripping/padding and global seqno rewriting affect key material used for comparison, exposure, and checksums. The file contains TODOs around timestamp implications for KV protection.

## Test signals

The file has sync points for constructor entry, iterator corruption injection, read-amp randomization, checksum length exposure, and value-pointer observation. Assertions cover restart invariants, separated-KV boundaries, global seqno assumptions, index decoding, and parallel key ordering assumptions. Relevant tests should exercise malformed footers, zero-restart/empty blocks, hash-index collision and no-entry cases, prefix-index absent prefixes, interpolation-vs-binary seek equivalence, reverse iteration with delta-encoded keys, separated-KV blocks, per-KV checksum failures, global seqno files, and timestamp persistence disabled.
