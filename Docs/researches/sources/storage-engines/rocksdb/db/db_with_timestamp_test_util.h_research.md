# sources/storage-engines/rocksdb/db/db_with_timestamp_test_util.h

## Purpose
`db_with_timestamp_test_util.h` declares the shared fixture and comparator utilities used by RocksDB's timestamp DB tests. It centralizes a timestamp-aware base class, deterministic key/timestamp encoders, and iterator assertion helpers, and defines the custom comparator used by tests that require a 16-byte two-part timestamp.

## Important APIs, Types, And Functions
`DBBasicTestWithTimestampBase` derives from `DBTestBase` and passes `env_do_fsync=true` to its base constructor, making timestamp tests run against a DB fixture with durable fsync behavior enabled. The constructor accepts the DB name so specialized fixtures can isolate their database directories.

The protected static helpers are `Key1(uint64_t)`, `KeyWithPrefix(std::string, uint64_t)`, and `ConvertStrToSlice(std::vector<std::string>&)`. The protected instance helper `Timestamp(uint64_t low, uint64_t high)` encodes the custom two-component timestamp format.

`TestComparator` derives from `Comparator` with a configurable `timestamp_size()`. It delegates user-key comparison to `BytewiseComparator()` after stripping timestamps when present. Its `Compare()` first compares keys without timestamps; if user keys are equal and timestamps are enabled, it compares timestamps and negates the timestamp comparison so larger/newer timestamps sort before smaller/older timestamps for the same user key.

`CompareWithoutTimestamp()` validates timestamp-bearing key lengths, strips timestamp suffixes when requested with `StripTimestampFromUserKey()`, and delegates to the bytewise comparator. `CompareTimestamp()` supports null timestamp slices, then decodes each timestamp as `{low, high}` fixed64 values and orders first by `high`, then by `low`.

The declared assertion helpers are `CheckIterUserEntry()` for public iterator entries and two `CheckIterEntry()` overloads for parsed internal keys, with or without an expected sequence number.

## Control Flow
The comparator control flow mirrors RocksDB's timestamped-key contract. For two keys, it compares the user-key portion first. Only when the user-key portions are equal does it inspect timestamp suffixes. Null timestamp slices are ordered below non-null slices, equal fixed-size timestamps compare equal, and non-null timestamp bytes are decoded into high/low components. `Compare()` reverses the timestamp comparison result so newer timestamps appear earlier in internal ordering for a given user key.

The base class exposes helpers as protected members so derived GoogleTest fixtures can write compact tests without leaking these helpers into unrelated test code.

## State And Persistence Behavior
The header itself stores no persistent state, but `TestComparator` defines how timestamped keys are ordered in memtables, SST files, range tombstones, file metadata boundaries, and compaction iterators. That ordering is part of the persisted data contract for tests using this comparator. If an SST is written with this comparator, reopen and compaction must use a comparator with the same timestamp size and comparison semantics.

The two-part timestamp format is test-specific and differs from RocksDB's U64 timestamp wrapper used in some compaction tests. Its high-then-low ordering allows tests to exercise nontrivial timestamp comparison while still producing fixed-size timestamp strings.

## Dependencies And Integration Points
The header includes `db/db_test_util.h`, `port/stack_trace.h`, and `test_util/testutil.h`. It integrates with RocksDB's `Comparator` interface, `BytewiseComparator`, timestamp-size support, `StripTimestampFromUserKey`, fixed64 decoding helpers, `Slice`, `Iterator`, `ValueType`, and `SequenceNumber`.

Downstream tests use this base fixture to configure `Options::comparator`, build timestamped write/read options, create mixed timestamped and non-timestamped column families, and assert iterator internals after compaction or history trimming.

## Risks
Comparator correctness is critical. Reversing the timestamp ordering in `Compare()` is deliberate; removing that negation would invert version ordering for equal user keys and break reads that expect newest eligible versions first. Mis-decoding `{low, high}` or changing comparison priority would silently change test semantics.

`CompareTimestamp()` copies timestamp slices into mutable buffers before `GetFixed64()` because decoding advances the slice pointer. Any mismatch between `timestamp_size()` and the encoded timestamp size asserts in tests and can also lead to invalid comparator behavior in DB operations.

Because the comparator delegates timestamp-stripped user-key comparison to bytewise ordering, tests using it should not assume locale, numeric, or custom collation semantics beyond the helper's encoded-key patterns.

## Test Signals
The header's behavior is validated indirectly by all timestamp tests that use `TestComparator`. Strong signals include correct ordering of multiple versions per key, exact iterator timestamps, correct file-boundary comparisons after reopen, correct handling of range tombstones and prefix extractors, and `InvalidArgument` results when timestamp sizes do not match the comparator's configured timestamp size.
