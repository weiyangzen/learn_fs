# sources/storage-engines/rocksdb/db/table_properties_collector.h

## Purpose

`table_properties_collector.h` declares the internal collector abstraction used by RocksDB table builders, adapters for public user-key collectors, a factory wrapper, and a timestamp min/max collector for user-defined timestamp keys.

## Important APIs, Types, and Functions

`InternalTblPropColl` defines `InternalAdd`, `BlockAdd`, `Finish`, `GetReadableProperties`, `NeedCompact`, and `Name`. `InternalTblPropCollFactory` creates collectors for a column family, level, total levels, and last-level sequence threshold. `UserKeyTablePropertiesCollector` wraps a public `TablePropertiesCollector`. `UserKeyTablePropertiesCollectorFactory` converts public factories to internal factories and fills `TablePropertiesCollectorFactory::Context`. `TimestampTablePropertiesCollector` extracts timestamps from internal keys and emits `rocksdb.timestamp_min` and `rocksdb.timestamp_max`.

## Control Flow

Table building constructs internal collectors through factories, feeds every internal key/value and block-size event into them, then calls `Finish` to populate user-collected property maps. The timestamp collector extracts the user key, validates it is long enough for the comparator timestamp size, compares timestamps through the comparator, and records min/max strings.

## State and Persistence Behavior

Collectors are per-table objects. User-collected properties become SST metadata. Timestamp collector state is two strings initialized to `kDisableUserTimestamp`; empty tables persist empty min/max. Collector factories retain shared pointers to user factories so option-owned factories remain alive.

## Dependencies and Integration Points

The header depends on `dbformat`, public comparator and table properties APIs. It is used by table builders, option sanitization, timestamp-aware compaction/read logic, and tests validating table property persistence across block-based and plain table formats.

## Risks and Test Signals

Risks include non-thread-safe factories despite the contract, timestamp comparator mismatch, short user keys causing corruption, old `Add`-only collectors needing compatibility, and `NeedCompact` propagation. Tests should cover factory context values, block callbacks, legacy collector mode, timestamp min/max with custom comparators, empty tables, and short-key corruption.
