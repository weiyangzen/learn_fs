# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/txn_subst.h

## Purpose
Supplies a small substitute for TokuDB transaction identifiers needed by the standalone locktree integration.

## Important APIs, Types, And Functions
Defines `TXNID` as `uint64_t`, sentinel constants `TXNID_NONE`, `TXNID_SHARED`, and `TXNID_ANY`, and `TxnidVector`, a `std::set<TXNID>` with a convenience `contains()` method.

## Control Flow
There is no dynamic control flow. The locktree code uses sentinels to distinguish no owner, multiple shared owners, and wildcard transaction matching.

## State And Persistence Behavior
`TxnidVector` owns an in-memory ordered set of transaction IDs. No durable transaction state is represented here.

## Dependencies And Integration Points
Includes `omt.h` and `<set>`. Range-tree status dumping uses `TXNID_SHARED` plus `TxnidVector` to enumerate owners. RocksDB casts `PessimisticTransaction*` values to `TXNID`, so this type bridges pointer identity into the imported locktree API.

## Risks And Edge Cases
Pointer-to-`uint64_t` transaction IDs are process-local and must never be persisted. The sentinel values reserve top unsigned values, so real IDs must avoid them. `contains()` is non-const, limiting use through const references.

## Test Signals
Signals are indirect through lock status and deadlock path reporting, especially shared-owner paths where `TXNID_SHARED` requires consulting the owner set.
