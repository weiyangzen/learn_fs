# sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index.h

## Purpose
Experimental secondary-index API maintained through the transaction layer, plus an iterator that queries secondary entries while exposing primary keys.

## Important APIs, Types, And Functions
`SecondaryIndex` configures primary/secondary CFs, identifies the primary column, optionally updates primary column values, computes/finalizes secondary key prefixes, and produces optional secondary values. `SecondaryIndexIterator` wraps an iterator and exposes `Seek`, `Next`, `Prev`, `PrepareValue`, `key`, `value`, `columns`, `timestamp`, `status`, and `GetProperty`.

## Control Flow, State, And Persistence
Transactional writes call applicable index callbacks before adding/removing secondary entries in the same transaction. Querying finalizes a search target prefix, seeks in the secondary CF, and strips that prefix from exposed primary keys. Persistent state is the secondary key-values stored in RocksDB.

## Dependencies And Integration Points
Depends on `Iterator`, `Slice`, `Status`, `WideColumns`, `ColumnFamilyHandle`, `optional`, and `variant`. Integrates with `TransactionDBOptions::secondary_indices`.

## Risks And Edge Cases
Experimental API. Applications must avoid primary/secondary key-space conflicts. Callback implementations must be deterministic and thread-safe after initialization. Non-OK callback statuses roll back related primary operations. Iterator validity depends on prefix matching and underlying iterator status.

## Test Signals
Cover insert/update/delete maintenance, plain and wide columns, same/different CFs, prefix finalization, iterator traversal, prepared values, callback errors, and concurrent transactions.
