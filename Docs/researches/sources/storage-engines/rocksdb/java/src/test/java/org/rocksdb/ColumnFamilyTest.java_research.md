# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ColumnFamilyTest.java

## Purpose

Integration coverage for Java column-family lifecycle and API variants: descriptors, listing, default family handles, opening DBs with multiple families, aliases for the default CF across DB flavors, fixed-buffer reads, write batches, iterators, multi-get, properties, dropped handles, binary names, Unicode names, and explicit handle destruction.

## Important APIs, control flow, and dependencies

The file uses `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `RocksDB.open`, `openReadOnly`, `OptimisticTransactionDB`, `TransactionDB`, `TtlDB`, `WriteBatch`, `WriteOptions`, `ReadOptions`, `RocksIterator`, `multiGetAsList`, `getProperty`, `getAggregatedLongProperty`, `dropColumnFamily`, `dropColumnFamilies`, and `destroyColumnFamilyHandle`. Tests open temporary DBs, create or list column families, perform per-CF writes/deletes/gets, then validate isolation and metadata. The default-CF synonym tests reopen DBs with `RocksDB.DEFAULT_COLUMN_FAMILY` in different descriptor positions and across transaction/TTL variants.

## State, persistence, risks, and test signals

Column-family metadata is persisted in the DB manifest and is verified through reopen/list operations. The suite also checks Java handle state after drops and explicit destruction. Risks include requiring the default CF in the descriptor list, using disposed handles, off-by-one errors in offset/length buffer reads, multi-get CF/key count mismatches, incorrect binary name handling, and missing cleanup of returned handles. Signals are value isolation by CF, exact returned byte arrays, exception expectations, property availability, iterator contents, and ownership flags.
