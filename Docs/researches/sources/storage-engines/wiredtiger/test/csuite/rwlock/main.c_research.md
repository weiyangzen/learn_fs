# sources/storage-engines/wiredtiger/test/csuite/rwlock/main.c

Purpose: load and correctness test for WiredTiger's internal reader/writer lock implementation, referencing HELP-4355 rwlock collapse under load. It can also be compiled against POSIX rwlocks with `USE_POSIX` for comparison.

Important APIs, types, and functions: global `WT_RWLOCK rwlock`, optional `pthread_rwlock_t p_rwlock`, `running`, and `shared_counter` coordinate the test. `main` parses standard options with defaults of 100 threads and one million operations per thread, opens WiredTiger with `session_max=1000`, initializes locks, starts a dump thread, starts worker threads, times completion, and cleans up. `thread_rwlock` opens a session, takes a write lock every `READS_PER_WRITE` operations and read locks otherwise, updates/checks `shared_counter`, and releases the lock. `thread_dump` prints internal rwlock fields once per second in verbose mode.

Control flow: workers loop from 1 to `opts->nops`, choose read versus write lock based on modulus, acquire either WiredTiger or POSIX lock depending on compile-time macro, do a small atomic increment to prevent optimization, check correctness by reading/updating `shared_counter` and yielding while holding the lock, then unlock. `main` joins all workers, stops the dump thread, destroys the POSIX lock, and calls `testutil_cleanup`.

State and persistence behavior: creates a WiredTiger home from parsed options and opens a connection mostly to obtain valid `WT_SESSION_IMPL` objects for lock operations. The shared correctness state is in memory (`shared_counter`). No table data is persisted.

Dependencies and integration points: depends on internal locking APIs `__wt_rwlock_init`, `__wt_readlock`, `__wt_writelock`, `__wt_readunlock`, `__wt_writeunlock`, atomics, yield, epoch timing, pthreads, and testutil option parsing. Registered as `test_rwlock` with a generated `WT_HOME` argument.

Risks: high default concurrency can be expensive and scheduler-sensitive. `opts->running = false` is set by each worker but the dump thread uses the separate global `running`; this is harmless but confusing. Correctness assertions depend on `CHECK_CORRECTNESS` and intentionally hold locks across `__wt_yield`, increasing contention.

Test signals: successful completion prints elapsed seconds and exits zero. Verbose mode prints periodic internal lock state, useful for diagnosing reader/writer queue collapse or starvation.
