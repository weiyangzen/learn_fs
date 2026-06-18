# sources/storage-engines/rocksdb/table/block_based/filter_policy_internal.h

## Purpose
Declares the internal filter-building and filter-reading abstractions behind RocksDB's public `FilterPolicy`, plus built-in Bloom-like policy classes that can read all built-in filter formats.

## Important APIs, Types, And Functions
`FilterBitsBuilder` defines `AddKey`, `AddKeyAndAlt`, `EstimateEntriesAdded`, `Finish`, corruption-aware `Finish`, `MaybePostVerify`, `ApproximateNumEntries`, `CalculateSpace`, and `EstimatedFpRate`. `FilterBitsReader` defines single and batch `MayMatch`. `BuiltinFilterBitsReader` adds `HashMayMatch`. `BuiltinFilterPolicy`, `ReadOnlyBuiltinFilterPolicy`, and `BloomLikeFilterPolicy` provide compatibility reading and builder creation. `BloomFilterPolicy`, `RibbonFilterPolicy`, and test-only `LegacyBloomFilterPolicy`, `FastLocalBloomFilterPolicy`, and `Standard128RibbonFilterPolicy` specialize builder selection.

## Control Flow
Table builders call a policy's `GetBuilderWithContext`, add whole keys and/or prefixes through the returned builder, then call `Finish` and optional post-verification. Table readers pass raw filter contents to `GetFilterBitsReader`, which returns an implementation-specific reader. Configuration code can create shared policies from strings via registered names.

## State And Persistence Behavior
The header itself has no persistence, but its contracts define how many entries are reported to table properties, how filter bytes are owned by a returned buffer, and how built-in filters remain compatible across format changes. `RibbonFilterPolicy` persists mutable option state in `bloom_before_level_` and registers it for option parsing.

## Dependencies And Integration Points
Depends on public `rocksdb/filter_policy.h`, block-based table options, cache-related context, and RocksDB configurable/customizable support. It is included by full-filter, partitioned-filter, mock table tests, and filter policy implementation.

## Risks And Edge Cases
Custom builders must honor no-false-negative semantics and accurately return zero entries only when no entries were added. `AddKeyAndAlt` has stricter de-duplication expectations than two independent `AddKey` calls. `MaybePostVerify` is optional but, when enabled, must not leave corrupted filters in use.

## Test Signals
Tests use the fixed implementation classes to force legacy Bloom, fast local Bloom, and Ribbon paths. Full-filter tests use custom plugin `FilterBitsBuilder`/`FilterBitsReader` implementations to verify the contract is not limited to built-in policies.
