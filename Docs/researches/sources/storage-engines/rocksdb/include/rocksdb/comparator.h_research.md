# sources/storage-engines/rocksdb/include/rocksdb/comparator.h

## Purpose

`comparator.h` defines RocksDB's public key ordering contract. Comparators impose the total order used by memtables, SSTables, range tombstones, indexes, iterators, compaction, transactions, and DB open compatibility checks. The header also exposes built-in bytewise and reverse-bytewise comparators, timestamp-aware variants, and utilities for encoding/decoding `uint64_t` user-defined timestamps.

## Important APIs, Types, and Functions

`CompareInterface` is the minimal abstraction with `Compare(const Slice&, const Slice&)`. `Comparator` derives from `Customizable` and `CompareInterface`, stores a `timestamp_size_`, and requires overrides for `Name()`, `Compare()`, `FindShortestSeparator()`, and `FindShortSuccessor()`. Optional overrides include `Equal()`, `IsSameLengthImmediateSuccessor()`, `CanKeysWithDifferentByteContentsBeEqual()`, `GetRootComparator()`, `GetMaxTimestamp()`, `GetMinTimestamp()`, `TimestampToString()`, `CompareTimestamp()`, `CompareWithoutTimestamp()`, and `EqualWithoutTimestamp()`.

Static/customization helpers include `Comparator::CreateFromString` and `Comparator::Type()`. Built-ins include `BytewiseComparator()`, `ReverseBytewiseComparator()`, `BytewiseComparatorWithU64Ts()`, and `ReverseBytewiseComparatorWithU64Ts()`. Timestamp helpers include `DecodeU64Ts`, `EncodeU64Ts`, `MaxU64Ts`, and `MinU64Ts`.

## Control Flow

RocksDB calls `Compare()` throughout read and write paths whenever user-key order matters. With user-defined timestamps enabled, `Compare()` compares the user-key plus timestamp, ordering newer timestamps first for the same user key. Internal code calls `CompareWithoutTimestamp()` when it needs user-key ordering independent of timestamp, such as range checks, file overlap checks, range tombstone handling, transaction lock ranges, and table iterator bounds.

Index construction calls `FindShortestSeparator()` and `FindShortSuccessor()` to shorten index keys without violating ordering. Prefix/auto-prefix code can call `IsSameLengthImmediateSuccessor()` for bound reasoning, but the header documents a bug constraint: it must only return true when no other keys starting with the successor are ordered before it. `CreateFromString` lets configuration parse known comparator names to built-in comparator objects.

## State and Persistence Behavior

Comparator choice is persistent DB metadata. The comparator `Name()` is stored/checked so opening an existing DB with an incompatible ordering fails instead of corrupting interpretation of SSTables. Any change to ordering must use a new comparator name. Timestamp size is comparator state that affects key layout and read/write semantics; built-in U64 timestamp comparators define max/min timestamp slices and encode/decode helpers.

The built-in comparator functions return immortal pointers that callers must not delete. `EncodeU64Ts` returns a `Slice` backed by caller-provided string storage, so its lifetime depends on `ts_buf`.

## Dependencies and Integration Points

The header depends on `<string>`, `customizable.h`, and `rocksdb_namespace.h`, with `Slice` forward-declared. It integrates broadly with `options.comparator`, memtable/table/index code, compaction pickers and outputs, range tombstone fragmentation, transaction lock managers, write-batch-with-index, SST file writer/reader, iterator timestamp APIs, and C API comparator constructors. Search signals show heavy use of `CompareWithoutTimestamp` in table, DB, compaction, transaction, and range tombstone code; implementation and built-in registration live in `util/comparator.cc`.

## Risks and Edge Cases

Comparator mistakes are severe: non-total or non-thread-safe ordering can corrupt DB behavior. Changing `Name()` incorrectly can either block valid opens or, worse, allow incompatible opens if the name is reused after ordering changes. Exceptions must not escape overrides. `CanKeysWithDifferentByteContentsBeEqual()` defaults true, which may disable or constrain hash-index optimizations unless overridden accurately. Timestamp-aware comparators must override timestamp min/max and compare-without-timestamp behavior coherently.

The `IsSameLengthImmediateSuccessor` bug note is important for auto-prefix mode; returning true too broadly can omit keys within iterator bounds. `FindShortestSeparator` and `FindShortSuccessor` may legally do nothing, but incorrect shortening can violate table index ordering. `EncodeU64Ts` lifetime is easy to misuse if the backing string is destroyed too early.

## Test Signals

Relevant tests include `db/comparator_db_test.cc` for successor behavior, `util/udt_util_test.cc` and `utilities/types_util_test.cc` for timestamp encoding/decoding, many `db/db_with_timestamp_*` and transaction timestamp tests for UDT semantics, table/block-based tests for timestamp-aware ordering, and `db/c.cc` plus C API tests for `rocksdb_comparator_with_ts_create`. Broad use of `CompareWithoutTimestamp` in compaction and range tombstone code means comparator changes need wider DB regression coverage.
