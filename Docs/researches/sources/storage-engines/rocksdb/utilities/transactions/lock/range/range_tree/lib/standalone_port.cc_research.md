# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/standalone_port.cc

## Purpose
Implements standalone glue that lets the imported Toku locktree build inside RocksDB without the rest of PerconaFT/TokuDB.

## Important APIs, Types, And Functions
Defines allocation wrappers `toku_free`, `toku_xmalloc`, `toku_xrealloc`, `toku_xmemdup`, and `toku_xcalloc`; global instrumentation keys such as `lock_request_m_wait_cond_key` and `manager_mutex_key`; `toku_memory_footprint`; `LTM_STATUS_S::init` and `destroy`; and bytewise key comparators `toku_keycompare` and `toku_builtin_compare_fun`.

## Control Flow
Allocation wrappers directly call libc allocation functions. Status initialization populates each `ltm_status.status` row with `TOKUFT_STATUS_INIT`, including lock memory, escalation, wait, timeout, and STO metrics. Comparator functions compare common prefixes with `memcmp`, then break ties by key length.

## State And Persistence Behavior
The file owns process-global instrumentation key variables and the global `ltm_status` object. State is in-memory status metadata only. It does not persist lock state or allocator state.

## Dependencies And Integration Points
Includes Toku compatibility headers, `ft-status`, memory helpers, and `dbt.h`. `RangeTreeLockManager::GetStatus()` later reads locktree status rows initialized through this path. Toku locktree code depends on these symbols during linking.

## Risks And Edge Cases
The `toku_x*` functions do not abort on allocation failure despite Toku naming convention comments, so callers assuming non-null allocation can crash later. `LTM_STATUS_S::destroy()` leaves partitioned counter destruction as a TODO. This file is excluded on Windows, matching the range-tree lock manager's `OS_WIN` guard.

## Test Signals
Link success for range-tree builds is the primary signal. Runtime signals include populated lock manager counters and correct bytewise comparator behavior for internal DBTs.
