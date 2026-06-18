# sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index_simple.h

## Purpose
Experimental simple secondary-index implementation that indexes a configured primary column value as-is.

## Important APIs, Types, And Functions
`SimpleSecondaryIndex` implements the `SecondaryIndex` interface and stores the primary column name plus primary/secondary column-family handles.

## Control Flow, State, And Persistence
For maintained primary writes, the implementation uses the primary column value as the secondary key component, finalizes the prefix, and lets the transaction layer persist secondary entries. Runtime state is only configuration and non-owning CF handles.

## Dependencies And Integration Points
Depends on `SecondaryIndex`; integrates with `TransactionDBOptions::secondary_indices` and `SecondaryIndexIterator`.

## Risks And Edge Cases
As-is values can make large or ambiguous secondary keys unless finalization encodes boundaries safely. Shared CFs require application-level key-space separation. Callback behavior must remain deterministic and thread-safe after initialization.

## Test Signals
Cover duplicate secondary values, updates/deletes, plain and wide-column indexing, prefix-boundary safety, shared/dedicated CFs, and iterator queries.
