# sources/storage-engines/rocksdb/include/rocksdb/utilities/options_util.h

## Purpose
Declares utilities for loading persisted RocksDB option files and checking supplied options against stored compatibility constraints.

## Important APIs, Types, And Functions
`LoadLatestOptions`, `LoadOptionsFromFile`, `GetLatestOptionsFileName`, and `CheckOptionsCompatibility` populate `DBOptions`, `ColumnFamilyDescriptor` vectors, and optionally a shared cache.

## Control Flow, State, And Persistence
`LoadLatestOptions` finds and parses the newest DB options file. `LoadOptionsFromFile` parses a specific file. Compatibility checking compares current inputs against persisted settings that cannot safely change. The utilities read persisted option files and produce in-memory options without mutating the DB.

## Dependencies And Integration Points
Depends on `ConfigOptions`, `DBOptions`, `ColumnFamilyDescriptor`, `Env`, `Cache`, and option parsers. Integrates with `ldb`, examples, DB open flows, object registry, and forward-compatible option loading.

## Risks And Edge Cases
Pointer-valued options are often defaulted and require caller repair. Missing files return `NotFound`, distinct from parse errors. Custom objects require registry registration. Newer option files may require `ignore_unknown_options`.

## Test Signals
Cover latest-file selection, missing files, malformed files, unknown options, object-registry loading, block table options, compatibility mismatches, and multi-CF loading.
