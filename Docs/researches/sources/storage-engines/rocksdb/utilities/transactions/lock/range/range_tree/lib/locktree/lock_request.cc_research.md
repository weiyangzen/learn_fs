# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/lock_request.cc

## Purpose
`lock_request.cc` implements pending lock acquisition, timed waits, retry/wakeup, deadlock detection, wait reporting, and waiter cancellation for range-lock requests.

## Important APIs, Types, And Functions
Key methods are `create()`, `destroy()`, `set()`, `start()`, `wait()`, `retry()`, `retry_all_lock_requests()`, `retry_all_lock_requests_info()`, `kill_waiter()`, and pending-list helpers. It uses `txnid_set` for conflict sets and `wfg` for deadlock detection.

## Control Flow
`start()` tries `locktree::acquire_write_lock()` or `acquire_read_lock()`. On `DB_LOCK_NOTGRANTED`, it copies endpoint DBTs before sleeping, marks itself pending, inserts into the locktree's sorted pending request list under `m_info->mutex`, and checks for deadlock. `wait()` retries once under the pending mutex, reports waits, then sleeps on an external condition until grant, timeout, or kill callback. Releases call `retry_all_lock_requests()` to coalesce retry work and broadcast successful waiters.

## State And Persistence Behavior
A request transitions through `UNINITIALIZED`, `INITIALIZED`, `PENDING`, `COMPLETE`, and `DESTROYED`. Pending requests own DBT endpoint copies if endpoints are finite. Counters for waits, timeouts, long waits, and wait time accumulate in `lt_lock_request_info`; no persistent state exists.

## Dependencies
It uses RocksDB-provided external mutex/condition wrappers, locktree APIs, transaction IDs, DBT helpers, current-time helpers, wait graph, and OMT sorted arrays.

## Integration Points
Higher-level range-lock manager code constructs these requests when immediate lock acquisition fails. `locktree_manager::iterate_pending_lock_requests()` and `kill_waiter()` inspect or manipulate the same pending request lists.

## Risks And Edge Cases
Pending-list operations assume unique txnid requests per locktree. Deadlock detection only includes transactions that currently have pending lock requests. `toku_external_mutex_trylock()` always locks in this port, so status collection may block despite trylock naming.

## Test Signals
Lock timeout tests, wait counter tests, waiter-access tests, deadlock-oriented point-lock tests through `AnyLockManagerTest`, and kill/wait callback paths are the important signals.
