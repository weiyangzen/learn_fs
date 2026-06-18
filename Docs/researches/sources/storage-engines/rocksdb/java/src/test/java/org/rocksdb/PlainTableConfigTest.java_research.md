## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PlainTableConfigTest.java

### Purpose

`PlainTableConfigTest` validates Java getter/setter bindings for `PlainTableConfig` and confirms installing it changes an `Options` object's table factory.

### Important APIs, Types, And Functions

It covers `setKeySize`, `setBloomBitsPerKey`, `setHashTableRatio`, `setIndexSparseness`, `setHugePageTlbSize`, `setEncodingType`, `setFullScanMode`, `setStoreIndexInFile`, `Options.setTableFormatConfig`, and `Options.tableFactoryName`.

### Control Flow

Each scalar test constructs a config, sets one field, and asserts the getter. The integration test attaches the config to `Options` and expects `tableFactoryName()` to be `PlainTable`.

### State And Persistence Behavior

Only option/config native state is mutated. No DB is opened, so table layout persistence is not exercised.

### Dependencies And Integration Points

This integrates `PlainTableConfig`, `EncodingType`, native table factory selection, and RocksDB native library loading.

### Risks And Edge Cases

- Defaults are not checked; only setter round trips are covered.
- The table factory name string is a stable contract used by Java tests but supplied by native code.

### Test Signals

Signals are exact getter values and `PlainTable` table factory name. Static research only; no test command was run.
