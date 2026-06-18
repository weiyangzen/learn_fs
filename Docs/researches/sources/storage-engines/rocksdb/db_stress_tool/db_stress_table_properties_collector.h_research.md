# sources/storage-engines/rocksdb/db_stress_tool/db_stress_table_properties_collector.h

## Purpose

`db_stress_table_properties_collector.h` defines a stress-only table-properties collector and factory. The collector ignores semantic key/value content, emits one synthetic user-collected property, and randomly marks SST files as needing compaction based on `FLAGS_mark_for_compaction_one_file_in`.

## Important APIs, Types, and Functions

- `DbStressTablePropertiesCollector : public TablePropertiesCollector` implements `AddUserKey()`, `BlockAdd()`, `Finish()`, `GetReadableProperties()`, `Name()`, and `NeedCompact()`.
- The constructor samples `need_compact_` once with `Random::GetTLSInstance()->OneInOpt(...)`.
- `Finish()` writes `db_stress_collector_property` as `keys_added;blocks_added;all_calls`.
- `GetReadableProperties()` returns the same property by calling `Finish()` through `const_cast`.
- `DbStressTablePropertiesCollectorFactory` creates a new collector per table build.

## Control Flow and State Behavior

During SST construction, `AddUserKey()` and `BlockAdd()` increment counters. `Finish()` emits the synthesized property. `NeedCompact()` returns the constructor's fixed random decision and increments the total-call counter. The counters are intentionally unsynchronized to expose any RocksDB bug that invokes collector methods concurrently despite collectors not being required to be thread-safe.

## Dependencies and Integration Points

The header depends on `rocksdb/table.h`, gflags compatibility, and thread-local random utilities. `db_stress_test_base.cc` installs this factory in `options.table_properties_collector_factories`, and `FLAGS_mark_for_compaction_one_file_in` is defined in `db_stress_gflags.cc`.

## Risks and Edge Cases

`GetReadableProperties()` mutates state through `const_cast`, so repeated readable-property requests can change the emitted call count. The factory returns a raw pointer as required by the RocksDB API. The behavior for zero or negative `mark_for_compaction_one_file_in` depends on `OneInOpt()` matching the flag documentation that compaction marking is disabled.

## Test Signals

Signals include successful SST builds with the synthetic property present, no sanitizer/race failures in collector callbacks, and compactions triggered when `--mark_for_compaction_one_file_in` is positive.
