## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptionsUtilTest.java

### Purpose

`OptionsUtilTest` verifies loading RocksDB OPTIONS files through Java and reconstructing DB options, CF descriptors, and block-based table format configuration.

### Important APIs, Types, And Functions

It uses `OptionsUtil.loadLatestOptions`, `OptionsUtil.loadOptionsFromFile`, `OptionsUtil.getLatestOptionsFileName`, `ConfigOptions`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `BlockBasedTableConfig`, `BloomFilter`, and `LoaderUnderTest`.

### Control Flow

Loader tests pass a strategy object that either loads the latest options by DB path or loads an explicit OPTIONS filename. `verifyOptions` creates a DB with a second CF and custom DB/CF settings, closes it, loads options back, and compares DB options and both CF descriptors. `verifyTableFormatOptions` repeats that pattern with a custom `BlockBasedTableConfig` and delegates detailed comparison to `verifyBlockBasedTableConfig`.

### State And Persistence Behavior

The file relies on RocksDB writing OPTIONS files to the DB directory. It then parses that persisted configuration into Java option objects, so it tests config file format compatibility rather than live DB data.

### Dependencies And Integration Points

This integrates `ConfigOptions` flags (`ignoreUnknownOptions`, `inputStringsEscaped`, `Env`), RocksDB option-file persistence, CF descriptor ordering, block-based table config parsing, and filter policy comparison.

### Risks And Edge Cases

- OPTIONS file format changes can break strict loading when `ignoreUnknownOptions(false)`.
- Some table config objects, especially cache instances, are intentionally not read back, so coverage excludes ownership-heavy fields.
- Loader variants with default `ConfigOptions` may behave differently from explicit escaped-string/env settings.

### Test Signals

Signals are a non-null `OPTIONS-*` latest filename, two loaded CF descriptors in expected order, exact DB/CF option values, and exact block-based table config fields. Static research only; no test command was run.
