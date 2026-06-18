# Research: sources/storage-engines/rocksdb/utilities/ttl/db_ttl_impl.h

## Purpose

This header declares the internal implementation of RocksDB's TTL database wrapper. It defines `DBWithTTLImpl`, `TtlIterator`, `TtlCompactionFilter`, `TtlCompactionFilterFactory`, `TtlMergeOperator`, and the `RegisterTtlObjects` C entry point used by the object registry. The declarations describe how the public `DBWithTTL` API is layered on top of a base `DB`, how TTL metadata is added/removed, and how compaction/merge/iterator behavior is adapted for timestamp-suffixed values.

## Important APIs, Types, And Functions

- `DBWithTTLImpl : public DBWithTTL` is the concrete stackable DB wrapper. It owns close idempotence state and overrides TTL-aware DB APIs.
- `DBWithTTLImpl::SanitizeOptions` is the static hook that wraps column-family options with TTL compaction filtering and merge behavior before DB or column-family creation.
- `DBWithTTLImpl::RegisterTtlClasses` registers TTL custom object factories once for option-string support.
- `Close`, destructor, and `GetBaseDB` define wrapper lifecycle and access to the underlying `DB`.
- `CreateColumnFamilyWithTtl` and `CreateColumnFamily` expose TTL-aware CF creation. The non-TTL overload defaults to TTL `0`.
- `Put`, `Merge`, and `Write` override write paths to add timestamp suffixes.
- `Get`, `MultiGet`, `KeyMayExist`, and `NewIterator` override read paths to strip timestamp suffixes.
- `IsStale`, `AppendTS`, `SanityCheckTimestamp`, and `StripTS` are static helpers for timestamp expiry, encoding, validation, and removal.
- `kTSLength` is the fixed timestamp suffix length (`sizeof(int32_t)`). `kMinTimestamp` guards against pre-feature/corrupt timestamps. `kMaxTimestamp` documents the signed-32-bit upper timestamp limit.
- `SetTtl` and `GetTtl` mutate/read the TTL on a column family's TTL compaction-filter factory.
- `TtlIterator : public Iterator` wraps a base iterator, delegates positioning/key/status calls, decodes `ttl_timestamp()`, and returns timestamp-stripped `value()`.
- `TtlCompactionFilter : public LayeredCompactionFilterBase` composes TTL expiry with an optional user compaction filter and exposes option validation/registration hooks.
- `TtlCompactionFilterFactory : public CompactionFilterFactory` stores mutable TTL, clock, and optional user factory; it creates per-compaction `TtlCompactionFilter` objects and exposes `Inner()` for customization introspection.
- `TtlMergeOperator : public MergeOperator` stores a user merge operator and clock, wraps full/partial merge, and exposes `Inner()` for customization introspection.
- `RegisterTtlObjects(ObjectLibrary&, const std::string&)` is declared `extern "C"` for dynamic/static object-library registration.

## Control Flow

The header defines a wrapper-oriented call graph. Open/create code in the `.cc` file sanitizes options first, then constructs a base `DB`, then wraps it in `DBWithTTLImpl`. Public write calls route through `DBWithTTLImpl::Write`, where timestamps are appended before forwarding to the base DB. Public read calls route to the base DB and then strip suffixes before returning to the user. Iterator reads create a `TtlIterator`, which delegates traversal to the base iterator and trims values lazily.

Compaction flow is declared as a layered filter: RocksDB asks `TtlCompactionFilterFactory::CreateCompactionFilter` for a filter, then `TtlCompactionFilter::Filter` decides whether to drop stale values before delegating to any user filter. Merge flow is declared through `TtlMergeOperator`, which makes the user's merge operator operate on logical values and reattaches TTL metadata afterward.

Option loading flow is represented by `PrepareOptions`, `ValidateOptions`, `Name`, `kClassName`, `IsInstanceOf`, and `Inner` declarations on the custom objects. These let RocksDB's customization registry instantiate, prepare, validate, compare, and introspect TTL wrappers.

## State And Persistence Behavior

`DBWithTTLImpl` itself only adds `closed_`, a process-local lifecycle flag. The persistent TTL state is the four-byte timestamp suffix appended to each stored value by implementation code. The static timestamp constants define the on-disk logical contract: every readable TTL value must be at least four bytes long and have a timestamp not older than `kMinTimestamp`.

`TtlIterator` owns the wrapped iterator pointer and deletes it in its destructor. It does not own value memory; `value()` returns a `Slice` pointing into the base iterator's value with its length shortened by `kTSLength`.

`TtlCompactionFilter` stores `ttl_` and a raw `SystemClock*` plus inherited user-filter ownership/state from `LayeredCompactionFilterBase`. `TtlCompactionFilterFactory` stores a mutable `ttl_`, raw clock pointer, and shared user filter factory. `TtlMergeOperator` stores a shared user merge operator and raw clock pointer. The raw clock pointers are expected to come from `Env`/`SystemClock` singletons or DB options and outlive the wrappers.

`SetTtl` changes the TTL value in the installed factory for future compactions; it does not change already-encoded timestamps or immediately delete old data. `GetTtl` reports the current factory value.

## Dependencies And Integration Points

This header includes:

- `db/db_impl/db_impl.h` for DB implementation utilities used by the TTL wrapper implementation.
- Public RocksDB APIs: `rocksdb/db.h`, `rocksdb/utilities/db_ttl.h`, `rocksdb/compaction_filter.h`, `rocksdb/merge_operator.h`, and `rocksdb/system_clock.h`.
- `utilities/compaction_filters/layered_compaction_filter_base.h` for user compaction-filter composition.
- `ObjectLibrary`/`ObjectRegistry` forward declarations for registry integration.

The exposed classes integrate with the public `DBWithTTL` API, RocksDB's stackable DB layer, the compaction filter and merge operator plugin systems, option serialization/deserialization, and iterator API. The `extern "C"` registration function is an integration point for object-library loading.

## Risks And Edge Cases

- `TtlIterator::value()` asserts timestamp validity instead of surfacing a `Status`, so corrupt TTL suffixes in iterator reads can trip debug assertions.
- `TtlIterator::ttl_timestamp()` assumes the current value has at least `kTSLength` bytes and does not validate `Valid()` or value length itself.
- The header exposes raw pointers for `SystemClock`, raw compaction filters, and wrapped iterators. Correct lifetime is enforced by usage patterns rather than types.
- `SetTtl` returns `void` and silently returns if no factory is available, while `GetTtl` can report invalid arguments or missing TTL factory. This asymmetry can hide configuration mistakes.
- `CreateColumnFamily` defaulting to TTL `0` means CFs created through the non-TTL overload are still timestamp-suffixed but never expire by TTL.
- The fixed `int32_t` timestamp format has a documented maximum of `2147483647`; callers and tests should account for the eventual overflow boundary.
- `IsInstanceOf` aliases `"Delete By TTL"` and `"Merge By TTL"` preserve legacy/customization names, so option-equivalence logic must handle both canonical and alias names.

## Test Signals

The declarations are exercised by `db_ttl_impl.cc` and by TTL tests that instantiate the wrappers through both direct DB APIs and object-registry strings. Important signals include successful `DBWithTTL::Open`, CF creation with TTL, option-string creation of `TtlCompactionFilter`, `TtlCompactionFilterFactory`, and `TtlMergeOperator`, validation failures when required inner objects or clocks are missing, iterator value trimming, stale-value compaction, mutable TTL changes, and correct composition with user merge operators and compaction filters.
