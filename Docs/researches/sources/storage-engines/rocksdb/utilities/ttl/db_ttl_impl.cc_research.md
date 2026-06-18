# Research: sources/storage-engines/rocksdb/utilities/ttl/db_ttl_impl.cc

## Purpose

This file implements RocksDB's `DBWithTTL` wrapper. The wrapper stores an internal 4-byte creation timestamp at the end of every value written through the TTL API, strips that timestamp from user-visible reads and iterators, and installs compaction filters that delete expired values during compaction. It also wraps user merge operators and compaction filters so they see timestamp-free values while TTL metadata remains preserved internally.

The implementation bridges public `DBWithTTL::Open`/column-family APIs, `StackableDB` forwarding, RocksDB option serialization/registry support, and the TTL-specific compaction/merge behavior declared in `db_ttl_impl.h`.

## Important APIs, Types, And Functions

- `TtlMergeOperator` wraps a user `MergeOperator`. `FullMergeV2` and `PartialMergeMulti` remove TTL timestamps from existing values and operands, delegate to the user operator, then append a fresh current timestamp to the merge result.
- `TtlMergeOperator::PrepareOptions` lazily fills `clock_` from `ConfigOptions::env`; `ValidateOptions` requires both a user merge operator and a system clock.
- `DBWithTTLImpl::SanitizeOptions` rewrites column-family options at open/create time. It wraps an existing raw compaction filter in `TtlCompactionFilter`, otherwise wraps/creates a `TtlCompactionFilterFactory`; it also wraps any merge operator in `TtlMergeOperator`.
- `TtlCompactionFilter` extends `LayeredCompactionFilterBase`. Its `Filter` first drops stale TTL values, then optionally delegates to the user compaction filter using the timestamp-stripped value. If the user filter changes the value, it appends the original timestamp to the replacement.
- `TtlCompactionFilterFactory` owns the active TTL and optional user compaction-filter factory. `CreateCompactionFilter` instantiates a `TtlCompactionFilter` with a user-created inner filter when available. `SetTtl`/`GetTtl` mutate and expose the live TTL.
- `RegisterTtlObjects` registers `TtlMergeOperator`, `TtlCompactionFilterFactory`, and `TtlCompactionFilter` constructors with an `ObjectLibrary`; `DBWithTTLImpl::RegisterTtlClasses` installs that library once in the default registry.
- `DBWithTTL::Open` has single-CF and multi-CF overloads. They validate TTL vector size, derive the system clock from `DBOptions::env` or default clock, sanitize each CF descriptor, open base RocksDB normally or read-only, then wrap the result in `DBWithTTLImpl`.
- `DBWithTTLImpl::AppendTS`, `SanityCheckTimestamp`, `IsStale`, and `StripTS` implement the timestamp encoding/checking/removal contract.
- `Put`, `Merge`, and `Write` intercept writes. `Write` iterates the caller's `WriteBatch`, appends timestamps to `PutCF` and `MergeCF` records, preserves deletes, range deletes, and log data, then writes the transformed batch to the underlying DB.
- `Get`, `MultiGet`, `KeyMayExist`, and `NewIterator` intercept reads. They strip timestamps from found values or return a `TtlIterator` that strips timestamps from iterator values.
- `Close` cancels background work, closes the base DB, deletes the default raw compaction filter pointer if one was installed, and sets an idempotence flag. The destructor calls `Close` if needed.

## Control Flow

Opening a TTL DB starts by registering TTL object factories. The multi-column-family `Open` checks `ttls.size() == column_families.size()`, chooses a clock, copies the CF descriptors, and calls `SanitizeOptions` for every CF. Sanitization ensures the underlying DB always receives timestamp-aware filters and merge operators. The base DB is opened through `DB::Open` or `DB::OpenForReadOnly`; on success the raw `DB` is moved into a new `DBWithTTLImpl`.

Writes are transformed at batch granularity. Public `Put` and `Merge` create a small `WriteBatch` and call `Write`; caller-supplied batches are handled by a local `WriteBatch::Handler`. For each put or merge record the handler calls `AppendTS`, then emits a corresponding record into `updates_ttl` with the same column-family id. Deletes and range deletes are forwarded unchanged. If timestamp acquisition fails, iteration stops with that status; otherwise the transformed batch is sent to `db_->Write`.

Reads delegate to the base DB first, then validate and strip TTL metadata. `Get` rejects the timestamp-returning overload, reads into `PinnableSlice`, checks the suffix length and minimum timestamp, then removes the suffix. `MultiGet` rejects the timestamp array overload, delegates to the base DB, then for every successful value moves/pins it locally, validates the timestamp, and strips it. `KeyMayExist` only strips the optional returned string when the base DB says a value was found.

Compaction filtering is deletion-first. `TtlCompactionFilter::Filter` calls `DBWithTTLImpl::IsStale`; stale values are dropped regardless of user filter. Fresh values are passed to the user filter without the timestamp. If the user filter requests a value rewrite, the TTL filter appends the original internal timestamp so the rewritten value remains readable by TTL readers.

Merge wrapping strips all operand timestamps before invoking the user merge operator. After successful full or partial merge, it appends the current timestamp, making merge output creation time equal to merge execution time. `existing_operand` outputs from `FullMergeV2` are copied into `new_value` before timestamping.

Iterator creation enforces `ReadOptions::io_activity` to be either unknown or `kDBIterator`, normalizes unknown to `kDBIterator`, then wraps the base iterator in `TtlIterator`. `TtlIterator::value()` asserts timestamp sanity and returns a slice shortened by four bytes; `ttl_timestamp()` exposes the decoded internal timestamp for callers that know they are using the wrapper.

Close is staged to avoid background compaction using filter state after wrapper teardown. It snapshots default options, cancels all background work with wait, closes the base DB, deletes the default `compaction_filter` raw pointer captured from options, and marks the wrapper closed.

## State And Persistence Behavior

TTL metadata is stored inline at the end of every value as a fixed-width little-endian `int32_t` generated from `SystemClock::GetCurrentTime`. This means all persisted SST/WAL/memtable values written through `DBWithTTL` contain user bytes plus a 4-byte timestamp suffix. Normal non-TTL RocksDB reads against the same data would see the suffix.

Expiration is not enforced at read time. `IsStale` is used by compaction filters, so stale keys are physically removed only when compaction processes them. A non-positive TTL means data is always fresh. If the clock cannot be read during stale checking, the value is treated as fresh to avoid accidental deletion.

`SanityCheckTimestamp` rejects values smaller than the timestamp suffix or values whose decoded timestamp predates `kMinTimestamp`, which helps catch corrupted data or an ordinary RocksDB opened incorrectly through TTL mode. `kMaxTimestamp` is declared in the header but not enforced here.

`SetTtl` mutates the TTL inside the installed `TtlCompactionFilterFactory` obtained from current column-family options. This affects future compaction-filter creation but does not rewrite already stored timestamps. `GetTtl` reads that factory value. If TTL was configured with a raw compaction filter rather than a factory, the static cast can yield no usable factory and `GetTtl` reports invalid configuration.

Object-registry state is process-global and registered once through `std::call_once`. Option-string serialization uses registered option metadata for TTL, inner filters, filter factories, and wrapped merge operators.

## Dependencies And Integration Points

This implementation depends on:

- `DBWithTTL`, `StackableDB`, `DB`, `ColumnFamilyHandle`, `WriteBatch`, `Iterator`, `PinnableSlice`, `ReadOptions`, and `WriteOptions` from RocksDB public APIs.
- `WriteBatchInternal` for emitting transformed records with original column-family ids.
- `SystemClock` and `Env` for timestamp generation and option preparation.
- `LayeredCompactionFilterBase` for composing TTL filtering with user compaction filters.
- `ObjectRegistry`, `ObjectLibrary`, `OptionTypeInfo`, and `RegisterOptions` for option-string construction and validation.
- `EncodeFixed32`/`DecodeFixed32` for timestamp serialization.
- `CancelAllBackgroundWork` from RocksDB DB utilities to quiesce compaction before close.

The main integration points are public `DBWithTTL::Open`, `CreateColumnFamilyWithTtl`, `SetTtl`, `GetTtl`, user-provided merge operators and compaction filters/factories, and RocksDB option loading via registry strings such as `TtlCompactionFilter`, `TtlCompactionFilterFactory`, and `TtlMergeOperator`.

## Risks And Edge Cases

- TTL is compaction-driven, so expired values can still be returned by `Get`, `MultiGet`, `KeyMayExist`, and iterators until a compaction drops them.
- The timestamp is a 32-bit signed wall-clock value. The code declares a 2038-era `kMaxTimestamp` but does not validate it in `AppendTS` or `SanityCheckTimestamp`; time overflow remains a long-term format risk.
- If the clock fails during writes or merges, user writes fail. If it fails during compaction stale checks, values are retained.
- `SanitizeOptions` wraps raw `compaction_filter` by allocating a new `TtlCompactionFilter` and later `Close` deletes only the default CF raw filter pointer captured from `GetOptions`. Ownership is subtle because RocksDB options historically use raw compaction-filter pointers.
- `SetTtl`/`GetTtl` assume the installed `compaction_filter_factory` is a `TtlCompactionFilterFactory`. When a TTL DB was sanitized around a raw `compaction_filter`, there may be no TTL factory to mutate.
- User compaction filters only see timestamp-free values. If they rewrite a value, the original timestamp is preserved, not refreshed.
- User merge output receives a fresh timestamp, which means merge compaction/read behavior can change the creation time of logically merged values.
- `MultiGet` intentionally ignores its `sorted_input` parameter when delegating to the base API overload visible here; any behavior dependent on sorted input is not preserved by this wrapper method.
- `TtlIterator::value()` asserts timestamp sanity rather than returning an error for corrupt timestamp suffixes, so corruption handling differs from `Get`/`MultiGet`.
- Opening a non-TTL database in TTL mode can report corruption on reads because ordinary values lack valid TTL suffixes.

## Test Signals

Relevant test coverage is in `utilities/ttl/ttl_test.cc` and related RocksDB DB tests. The option tests load `TtlCompactionFilter`, `TtlCompactionFilterFactory`, and `TtlMergeOperator` by registry string, check TTL option values, validate nested dummy filters/factories/operators, verify `ToString`/`CreateFromString` round trips, and confirm `TtlMergeOperator` without a registered user operator fails validation.

Behavioral TTL tests should cover writes appending timestamps, reads stripping them, stale data disappearing after compaction rather than immediately, non-positive TTL retaining data, column-family-specific TTLs, `SetTtl`/`GetTtl`, user compaction filter composition, user merge operator composition, corrupted or missing timestamp suffixes, read-only open, multiple column-family open with mismatched TTL vector rejection, write batch preservation of deletes/range deletes/log data, and close/destructor idempotence.
