# sources/storage-engines/rocksdb/options/cf_options.cc

## Purpose
`cf_options.cc` implements RocksDB column-family option registration, parsing, serialization, comparison adapters, and derived mutable column-family calculations. It bridges public `ColumnFamilyOptions`/`Options` structs with `Configurable`/`OptionTypeInfo` infrastructure used by options files, `SetOptions`, and object-registry-backed factories. Deprecated option names are retained so old `OPTIONS` files remain readable.

## Important APIs, Types, and Functions
Key functions and types include `ParseCompressionOptions`, `TableFactoryParseFn`, `CFOptionsAsConfigurable`, `ImmutableCFOptions` and `ImmutableOptions` constructors, `MultiplyCheckOverflow`, `MaxFileSizeForLevel`, `MaxFileSizeForL0MetaPin`, `MutableCFOptions::RefreshDerivedOptions`, `MutableCFOptions::Dump`, `GetMutableOptionsFromStrings`, and `GetStringFromMutableCFOptions`. The central contracts are `cf_mutable_options_type_info` and `cf_immutable_options_type_info`, plus nested maps for compression, FIFO compaction, universal compaction, and file-temperature thresholds.

## Control Flow
Parsing is metadata-driven through `OptionTypeInfo` offsets and flags. `ConfigurableCFOptions::ConfigureOptions` delegates to generic configuration, updates a full `ColumnFamilyOptions` from mutable and immutable snapshots, and prepares nested options. `TableFactoryParseFn` first tries mutable-only changes on the existing factory; otherwise it clones or creates the proper block/plain factory, configures the clone, and swaps the shared pointer only on success. Derived sizing is refreshed by filling `max_file_size` per level and using overflow-safe multiplication.

## State and Persistence Behavior
This file defines the serialized names and backward-compatibility behavior for persisted RocksDB options. Failed mutable parsing restores `base_options`; table-factory updates avoid publishing partial clones. Raw immutable pointers are non-owning snapshots, while shared pointers preserve object lifetimes from public option structs.

## Dependencies and Integration Points
It depends on options helpers/parser, configurable helpers, RocksDB public options, table factories, caches, merge operators, compaction filters, slice transforms, compression utilities, logging, and `ObjectRegistry`. It is used by DB open/options-file parsing, `SetOptions`, compaction sizing, blob configuration, option logging, and sanity comparison.

## Risks
Offset maps must stay synchronized with struct fields. Backward-compatible parsers can hide malformed legacy input if not tested. The table-factory clone/swap pattern is important for concurrent readers. Forgetting `RefreshDerivedOptions` after size-related mutations can leave stale compaction file-size state.

## Test Signals
`configurable_test.cc` and `customizable_test.cc` exercise CF wrappers, table factory creation, mutable-only updates, nested object serialization, and object registry loading. Wider RocksDB options-file tests provide additional compatibility coverage.
