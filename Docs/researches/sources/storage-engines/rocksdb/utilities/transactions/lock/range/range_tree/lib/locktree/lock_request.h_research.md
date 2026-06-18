# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/lock_request.h

## Purpose
`lock_request.h` declares the object that represents one potentially blocking range-lock acquisition and the wait-reporting structures used by callbacks.

## Important APIs, Types, And Functions
`lock_wait_info` records the locktree, waiting transaction, opaque extra pointer, and waited-on transaction IDs; `lock_wait_infos` is a vector of these. `lock_request::type` distinguishes `READ` and `WRITE`. Public APIs cover lifecycle, request reset, `start()`, timed `wait()`, endpoint/txnid accessors, static retry functions, test callbacks, extra access, and waiter killing.

## Control Flow
The documented flow is initialize, set request parameters, start immediate acquisition, optionally do other work, wait on a timed condition if pending, and destroy when no longer pending. Static retry functions are called after lock release to wake newly grantable requests.

## State And Persistence Behavior
Private fields store txnid, conflict txnid, start time, borrowed or copied endpoints, request type, owning `locktree`, completion code, state enum, external condition variable, big-transaction flag, locktree request-info pointer, extra pointer, and optional deadlock callback.

## Dependencies
It includes DBT/status definitions, comparator declarations, external pthread wrappers, `locktree`, `txnid_set`, and `wfg`. It uses `std::vector` and `std::function` via included headers.

## Integration Points
`locktree_manager` exposes pending requests and can kill waiters. RocksDB transaction lock manager code maps lock timeouts and deadlocks from this class into `Status` values.

## Risks And Edge Cases
The class is manually stateful and reusable, so callers must not destroy while pending or reuse without `set()`. Endpoint copies are made only when entering pending state; immediate acquisitions borrow caller DBTs. Test callback hooks can alter timing-sensitive behavior.

## Test Signals
Tests should cover immediate grant, timeout, deadlock, retry-after-release, killed waiter, wait callback contents, and request reuse after completion.
