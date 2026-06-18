# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/SeedShardServers.h

## Purpose
This small header declares the helper that seeds the initial shard-server mappings into the first database transaction.

## Important APIs, Types, And Functions
`seedShardServers(Arena& arena, CommitTransactionRef& tr, std::vector<StorageServerInterface> servers)` mutates a commit transaction to establish initial key/server assignments.

## Control Flow
Master initialization passes an arena, commit transaction, and recruited seed storage servers. The implementation writes the required system-key mutations into the transaction.

## State And Persistence Behavior
The function creates durable initial system keyspace state when the first transaction commits. It has no state of its own.

## Dependencies And Integration Points
It depends on commit transaction and storage-server interface types. It is called from initial cluster creation/recovery paths before ordinary `addStorageServer` flows are used.

## Risks And Edge Cases
Incorrect seeding can leave system key ranges unassigned or inconsistently replicated. The arena must outlive mutations stored in the commit transaction.

## Test Signals
Initial database creation tests should verify all keyspace ranges are assigned to seed servers, storage server tags are correct, and recovery can read the resulting system keyspace.
