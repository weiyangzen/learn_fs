# sources/storage-engines/rocksdb/options/cf_options.h

## Purpose
`cf_options.h` declares internal RocksDB column-family option snapshots. It separates immutable lifetime-long fields from mutable runtime fields and declares helpers for derived compaction/file-size behavior and string conversion.

## Important APIs, Types, and Functions
`ImmutableCFOptions` stores compaction style/priority, comparators, merge operators, filters, memtable factory, bloom locality, level counts, consistency flags, CF paths, blob direct-write settings, timestamp persistence, ingest-behind allowance, and batch lookup optimization. `ImmutableOptions` combines immutable DB and CF snapshots. `MutableCFOptions` stores mutable memtable, compaction, blob, compression, temperature, protection, verification, and iterator controls. Public helpers include `RefreshDerivedOptions`, `MaxBytesMultiplerAdditional`, `Dump`, equality, `MultiplyCheckOverflow`, `MaxFileSizeForLevel`, `MaxFileSizeForL0MetaPin`, `GetStringFromMutableCFOptions`, and `GetMutableOptionsFromStrings`.

## Control Flow
Construction from `ColumnFamilyOptions` copies public fields and immediately calls `RefreshDerivedOptions(options.num_levels, options.compaction_style)`. Callers mutating relevant fields later must refresh derived values. Immutable construction snapshots raw non-owning pointers and shared owning references from the public options.

## State and Persistence Behavior
The header defines in-memory state. Persistence is handled by `cf_options.cc` serializers. `max_file_size` is derived state, not a primary persisted option. Shared pointers keep factories/managers/operators alive; raw comparator and compaction-filter pointers remain non-owning.

## Dependencies and Integration Points
Dependencies include `db/dbformat.h`, `options/db_options.h`, `rocksdb/options.h`, and compression utilities. The structs feed memtable creation, compaction picking, flush/write throttling, blob handling, iterators, option logging, and `ConfigOptions` parsing.

## Risks
Adding fields requires updates in constructors, default initialization, option maps, logging if needed, and derived refresh logic if relevant. Drift between public `ColumnFamilyOptions`, `MutableCFOptions`, and metadata maps can break parsing or runtime behavior.

## Test Signals
Generic configurable tests and broader RocksDB option tests exercise these declarations through `CFOptionsAsConfigurable`, mutable option parsing, and debug helpers for detecting immutable entries in mutable maps.
