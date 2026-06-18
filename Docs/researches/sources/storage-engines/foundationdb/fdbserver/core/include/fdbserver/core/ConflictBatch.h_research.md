# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ConflictBatch.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ConflictBatch.h

Purpose: defines compact commit-result codes for conflict batch processing.

Important type: `ConflictBatchStatus::TransactionCommitResult` with `TransactionConflict`, `TransactionTooOld`, reserved `TransactionUnusedResultValue1`, `TransactionCommitted`, and `TransactionLockReject`.

Control flow and state: this header contains only enum constants stored as `uint8_t`. Values are part of an inter-component contract and should be treated as stable.

Dependencies and integration: depends only on `<cstdint>`. Commit proxy/resolver/client commit result paths can use the enum to encode conflict-batch outcomes.

Risks and tests: changing numeric order can break serialized or compact result interpretation. Tests should cover mapping from transaction outcome to enum value and any wire/storage encoding that relies on the `uint8_t` values.
