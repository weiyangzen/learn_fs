# sources/storage-engines/rocksdb/db/table_properties_collector.cc

## Purpose

`table_properties_collector.cc` implements adapter logic between internal-key table building and user-facing table property collectors, plus helpers for reading collected delete and merge counters from user-collected properties.

## Important APIs, Types, and Functions

`UserKeyTablePropertiesCollector::InternalAdd` parses an internal key and calls the wrapped `TablePropertiesCollector::AddUserKey` with user key, entry type, sequence, value, and current file size. `BlockAdd`, `Finish`, and `GetReadableProperties` delegate to the wrapped collector. The anonymous `GetUint64Property` decodes a varint64 property and reports presence. `GetDeletedKeys` and `GetMergeOperands` read `TablePropertiesNames::kDeletedKeys` and `kMergeOperands`.

## Control Flow

During table building, internal keys are fed into `InternalAdd`; parse failures return a non-OK status and stop/poison collection. Successful parses convert internal value types to public `EntryType` before delegation. Finish-time properties are whatever the wrapped collector emits. Read helpers are defensive: absent properties return zero and `property_present=false` where applicable; malformed varints also decode to zero.

## State and Persistence Behavior

The adapter owns a `std::unique_ptr<TablePropertiesCollector>`. It writes no files directly, but its output becomes persisted user-collected table properties in SST metadata blocks. The helper functions interpret those persisted properties after tables are read.

## Dependencies and Integration Points

The file depends on `dbformat`, varint coding, string utilities, and the public table properties APIs. `ColumnFamilyData` wraps user collector factories into internal collector factories; table builders call these collectors; compaction and property APIs later inspect the emitted properties.

## Risks and Test Signals

Risks include internal-key parse errors, incorrect mapping from RocksDB value types to public entry types, silent zero on malformed varints, and user collectors assuming they receive internal rather than user keys. Tests should cover puts, deletes, single deletes, merges, malformed internal keys, malformed property values, and readable-property passthrough.
