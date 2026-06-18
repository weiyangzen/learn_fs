# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TtlDB.java

## Purpose
`TtlDB` is the Java wrapper for RocksDB databases opened with time-to-live semantics. It extends `RocksDB` and ensures values are interpreted with internal timestamp suffixes so expired entries can be removed during compaction.

## Important APIs and Types
Static `open` overloads support default-column-family TTL and multi-column-family TTL lists. `createColumnFamilyWithTtl` creates TTL-enabled column families. `closeE()` closes with exception reporting, while `close()` closes owned column-family handles and suppresses close errors.

## Control Flow, State, and Persistence
The single-CF `open` calls native `open`, stores the options object, and stores the default column-family handle. The multi-CF `open` validates `columnFamilyDescriptors.size() == ttlValues.size()`, extracts names and option handles, requires the default column family, converts boxed TTLs to `int[]`, calls `openCF`, wraps returned handles, records owned handles, and stores the default handle by descriptor index. TTL state is persisted in values by native code via timestamp suffixing; expired entries are removed only during compaction, and read-only opens do not compact.

## Dependencies and Integration Points
Dependencies include `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `RocksDB.DEFAULT_COLUMN_FAMILY`, native `open/openCF/createColumnFamilyWithTtl/closeDatabase`, and inherited RocksDB handle management.

## Risks and Test Signals
Opening a TTL DB later through plain `RocksDB.open` can expose timestamp-suffixed values and disable TTL behavior. A small positive TTL can remove most data quickly, and expired values may remain visible until compaction. The Java code also assumes `columnFamilyHandles.get(defaultColumnFamilyIndex)` exists after wrapping native handles. This subset has no direct `TtlDB` test; coverage is mostly contract documentation and native integration.
