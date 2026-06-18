# sources/storage-engines/rocksdb/include/rocksdb/slice_transform.h

Purpose: This header defines the pluggable prefix/key transformation interface used most commonly for prefix Bloom filters and prefix seek optimization. It lets a column family map keys to comparable prefixes under documented safety constraints.

Important APIs and types: `SliceTransform` extends `Customizable`. It declares `Name()`, static `Type()`, static `CreateFromString()`, `AsString()`, pure virtual `Transform(const Slice&)`, pure virtual `InDomain(const Slice&)`, optional `FullLengthEnabled(size_t*)`, and optional `SameResultWhenAppended(const Slice&)`. Factories `NewFixedPrefixTransform(size_t)`, `NewCappedPrefixTransform(size_t)`, and `NewNoopTransform()` create common extractors.

Control flow: RocksDB checks `InDomain()` before adding/querying prefix Bloom entries. If true, it calls `Transform()` to derive the prefix. `FullLengthEnabled()` gives auto-prefix-mode code a maximum prefix length for recognizing upper-bound successor cases. `SameResultWhenAppended()` is mostly a user-facing safety check for seeking to a raw prefix without total-order seek.

State and persistence behavior: Transform objects are runtime configuration. Their names and semantics matter across DB reopen because existing SST filter/index data was built using prior extractor behavior. The header itself persists nothing, but changing extractor semantics can make persisted filters unsafe or ineffective.

Dependencies and integration points: It depends on `Customizable`, `rocksdb_namespace.h`, and `Slice`. `ColumnFamilyOptions::prefix_extractor`, block-based table filters, memtable prefix bloom, iterators, Gets, MultiGets, and option-string parsing use this interface.

Risks and edge cases: Implementations must not throw. Prefix extractors must satisfy the comparator-contiguity requirements documented in `options.h`; otherwise range scans with prefix filters can hide existing keys. `FullLengthEnabled()` and `auto_prefix_mode` have documented limitations around short keys. Returning true from `SameResultWhenAppended()` when not guaranteed can lead users to issue unsafe prefix seeks.

Test signals: Tests should verify transform/domain behavior for fixed, capped, and noop extractors; option-string creation and `AsString()` output; prefix Bloom correctness for in-domain/out-of-domain keys; total-order versus prefix seek equivalence; and unsafe extractor cases being rejected or documented by integration tests.
