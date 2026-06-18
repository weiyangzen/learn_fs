# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TSSMappingUtil.h

## Purpose
This header declares helpers for reading the current test storage server (TSS) to storage server mapping from system keyspace.

## Important APIs, Types, And Functions
`readTSSMappingRYW` reads the mapping through a `ReadYourWritesTransaction`; `readTSSMapping` reads it through a lower-level `Transaction`. Both fill `std::map<UID, StorageServerInterface>*`.

## Control Flow
Data movement or recruitment code calls the appropriate helper within an existing transaction, then uses the resulting map to account for TSS pairings.

## State And Persistence Behavior
The functions read persistent system keyspace mapping data but do not declare state of their own.

## Dependencies And Integration Points
It depends on RYW transactions and storage-server interfaces. It integrates with `MoveKeys`, TSS recruitment/removal, DD, and testing of storage shadowing.

## Risks And Edge Cases
Callers must pass a live transaction and handle retries. Stale mappings can lead to incorrect TSS pairing during movement or removal.

## Test Signals
Tests should validate mapping reads under both transaction types, empty mappings, TSS add/remove transitions, and retry behavior during concurrent mapping updates.
