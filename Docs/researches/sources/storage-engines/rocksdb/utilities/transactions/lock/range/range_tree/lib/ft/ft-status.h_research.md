# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/ft/ft-status.h

## Purpose
`ft-status.h` declares the locktree-manager status table used to export memory, escalation, pending request, single-transaction optimization, and wait counters from the range-lock subsystem.

## Important APIs, Types, And Functions
`LTM_STATUS_S` enumerates rows from `LTM_SIZE_CURRENT` through `LTM_LONG_WAIT_ESCALATION_TIME`, with `LTM_STATUS_NUM_ROWS` as the bound. It stores `TOKU_ENGINE_STATUS_ROW_S status[...]`, has `init()` and `destroy()`, and tracks `m_initialized`.

`LTM_STATUS` is a pointer alias. `ltm_status` is an extern singleton, `LTM_STATUS_VAL(x)` indexes numeric status values, and `toku_status_init()` / `toku_status_destroy()` are thin lifecycle declarations.

## Control Flow
This header has no implementation control flow. `locktree_manager::get_status()` calls `ltm_status.init()`, fills `LTM_STATUS_VAL(...)` fields, and assigns the singleton to the caller's status pointer.

## State And Persistence Behavior
The status rows are process-local telemetry. They are recomputed from in-memory manager and locktree counters and are not persisted. `m_initialized` prevents repeated row metadata setup in the implementation.

## Dependencies
It depends on `db.h`, race-tool annotations, and the local status utility. The status row shape intentionally mirrors PerconaFT/TokuDB interfaces even though RocksDB exposes a smaller public status struct elsewhere.

## Integration Points
`manager.cc` writes these rows; `treenode.h` includes this header for substituted transaction/status types. Range-lock manager handle status methods ultimately surface subsets of these counters to RocksDB tests and callers.

## Risks And Edge Cases
The singleton makes status collection global, so callers should treat it as a snapshot buffer rather than independent per-manager storage. New counters need enum, row initialization, and manager fill logic kept in sync.

## Test Signals
`BasicLockEscalation`, `LockWaitCount`, and `MultipleTrxLockStatusData` exercise corresponding memory, escalation, and wait/status surfaces indirectly.
