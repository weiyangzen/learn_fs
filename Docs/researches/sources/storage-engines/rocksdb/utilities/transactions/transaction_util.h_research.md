# sources/storage-engines/rocksdb/utilities/transactions/transaction_util.h

## Purpose
This header declares the transaction conflict-validation utility API shared by RocksDB transaction implementations. It documents how a transaction verifies that keys it read or locked have not been modified after its snapshot sequence, and how optional user-defined timestamp validation participates in that decision.

## Important APIs, Types, and Functions
`TransactionUtil` is a static utility class. It forward-declares `DBImpl`, `SuperVersion`, and `WriteBatchWithIndex`, and includes the status, slice, DB, type, read-callback, dbformat, and lock-tracker definitions needed by the declarations.

`CheckKeyForConflicts()` validates one key in one column family against a snapshot sequence and optional timestamp. Its parameters identify the DB implementation, public column-family handle, key string, `snap_seq`, optional timestamp pointer, `cache_only` behavior, optional `ReadCallback`, optional `min_uncommitted`, and `enable_udt_validation`. The comment defines expected outcomes: `OK` when no conflict is found, `Busy` for conflicting writes, and another error for unexpected failures or insufficient history.

`CheckKeysForConflicts()` validates all point locks tracked by a `LockTracker`. The header documents important preconditions: it should run on the write thread or while the mutex is held, and the tracker must support point locks.

Private `CheckKey()` is the internal primitive used by both public APIs. Its comment explains ordered and unordered visibility semantics. With no `snap_checker`, commits are sequence ordered and any sequence greater than `snap_seq` conflicts. With `snap_checker`, commits may not be in sequence-number order: sequences below `min_uncommitted` cannot conflict, sequences above `snap_seq` are conflict candidates, and sequences in the middle require callback visibility checks. The comment also states timestamp validation detects conflict when a key has an operation timestamp greater than the supplied read timestamp.

## Control Flow
The header establishes a two-level design: public APIs acquire or iterate DB state and then call the private `CheckKey()` primitive with enough context to avoid duplicating validation rules. Single-key callers pass a column family and key. Multi-key callers pass a `LockTracker`, and the implementation is responsible for iterating tracked column families and keys. Timestamp checks are optional and controlled separately from sequence checks so non-UDT and UDT-disabled callers can reuse the same path.

## State and Persistence Behavior
The API is read-only from the caller's perspective. It inspects DB versions, memtable history, latest key sequence numbers, and optionally persisted table state to decide whether validation is possible and whether a conflict exists. The `cache_only` flag is a persistence-boundary control: true forbids SST reads and can produce a retryable inability to validate when memtable history is insufficient.

## Dependencies and Integration Points
The declarations sit between transaction implementations and core DB internals. They expose core transaction validation to pessimistic transactions, optimistic transaction lock tracking, write-prepared visibility callbacks, and timestamp-aware write-committed validation. `ReadCallback` is the integration point for commit-order visibility; `LockTracker` is the integration point for collected point locks; comparator timestamp support is used by the implementation when `enable_udt_validation` is true.

## Risks and Edge Cases
The comments encode subtle correctness rules. Callers using `min_uncommitted` must also supply a `snap_checker`; otherwise visibility in unordered commit modes cannot be determined safely. Callers must pass timestamps whose size matches the column-family comparator. `CheckKeysForConflicts()` currently documents sequence-based behavior for tracked point locks, while timestamp conflict checking for that path is not advertised as complete. Misusing `cache_only` can turn otherwise resolvable conflict checks into `TryAgain` errors.

## Test Signals
The header is validated indirectly through transaction suites that call public transaction APIs rather than `TransactionUtil` directly. Timestamped write-committed tests cover UDT conflict behavior through `GetForUpdate()` and `CheckKeysForConflicts`-related paths, while optimistic and pessimistic transaction tests cover sequence-number based conflict detection and lock tracker iteration.
