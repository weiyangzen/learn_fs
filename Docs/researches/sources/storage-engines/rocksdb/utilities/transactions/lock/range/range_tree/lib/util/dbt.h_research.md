# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/dbt.h

## Purpose
Declares the DBT helper API used by the standalone Toku locktree code.

## Important APIs, Types, And Functions
The header declares initialization, fill, duplication, clone, destroy, simple DBT cleanup, positive/negative infinity sentinels, infinity/empty checks, infinity comparison, and pointer equality helpers.

## Control Flow
As a declaration header, it has no runtime flow. Its comments document ownership expectations: some helpers only reference caller memory while others allocate and require `toku_destroy_dbt`.

## State And Persistence Behavior
The declared API manipulates in-memory `DBT` and `simple_dbt` structures only.

## Dependencies And Integration Points
Includes the local `db.h` compatibility header. It is included by `standalone_port.cc`, locktree code, range buffers, and RocksDB's range-tree manager/tracker bridge.

## Risks And Edge Cases
The API is easy to misuse because ownership is encoded in flags and several helpers return DBTs pointing at external memory. Infinite DBTs are pointer sentinels, so callers must preserve sentinel identity.

## Test Signals
Compile coverage plus range lock acquisition/release tests validate the header contract. Dedicated tests should assert ownership and sentinel behavior across declarations and implementation.
