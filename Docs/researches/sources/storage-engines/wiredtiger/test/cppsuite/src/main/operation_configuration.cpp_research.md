# sources/storage-engines/wiredtiger/test/cppsuite/src/main/operation_configuration.cpp

## Purpose
Maps configured `thread_type` values to callable `database_operation` member functions so workload threads can execute the correct operation polymorphically.

## Important APIs, Types, And Functions
The constructor stores the source `configuration`, operation `thread_type`, and configured `THREAD_COUNT`. `get_func(database_operation *dbo)` returns a `std::function<void(thread_worker *)>` bound to the matching virtual operation method.

## Control Flow
`get_func` switches over all known `thread_type` enumerators: `BACKGROUND_COMPACT`, `CHECKPOINT`, `CUSTOM`, `INSERT`, `READ`, `REMOVE`, and `UPDATE`. Each case uses `std::bind` with the supplied `database_operation` instance and a `thread_worker *` placeholder. An unexpected enum value aborts via `testutil_die(EINVAL, ...)`.

## State And Persistence Behavior
The file does not directly mutate database state. It influences persistence by selecting which operation loop a thread will execute and therefore which WiredTiger APIs, tracking rows, and timestamps are used.

## Dependencies And Integration Points
Depends on `operation_configuration.h`, `constants.h`, `database_operation`, and `thread_worker`. It is used by the workload manager layer when converting parsed test configuration into runnable thread functions.

## Risks And Test Signals
Adding a new `thread_type` requires updating this switch; otherwise the framework aborts at runtime. The returned `std::function` captures `dbo` by pointer, so the owning `test` object must outlive operation threads.
