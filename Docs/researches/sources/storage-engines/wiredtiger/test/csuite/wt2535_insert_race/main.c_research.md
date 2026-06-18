# sources/storage-engines/wiredtiger/test/csuite/wt2535_insert_race/main.c

Purpose: this test reproduces WT-2535 by checking for lost updates when many threads repeatedly read-modify-write the same record. It is a correctness test: the final value must equal `nthreads * nrecords`.

Important APIs, types, and functions: it uses `WT_SESSION` snapshot transactions, `WT_CURSOR::search`, `WT_CURSOR::update`, `WT_ROLLBACK` retry handling, pthreads, and an atomic readiness barrier. `get_value` wraps the variadic cursor getter for a `uint64_t` value. `thread_insert_race` performs the concurrent increment loop. `main` creates the single-record table and verifies the final value.

Control flow: `main` defaults to 20 threads and 100,000 operations per thread, parses options including row or column table type, creates the table with `value_format=Q`, inserts key 1 with value 0, starts all threads, joins them, then reads key 1 and compares it to the expected count. Each worker opens its own session/cursor, waits until all workers are ready, then loops. On each iteration it begins a snapshot transaction, reads the current value, updates it to `value + 1`, commits, and retries the same iteration if update returns `WT_ROLLBACK`.

State and persistence behavior: the durable state is a single integer record in a temporary WiredTiger table. The readiness barrier uses `ready_counter` with memory barriers so the race starts concurrently. Transaction retry behavior is the key state transition: rollbacks must not lose an increment because the loop decrements `i` and retries.

Dependencies and integration points: the smoke wrapper runs both row and column variants via `-t r` and `-t c`. The test uses common parse/cleanup helpers and statistics logging.

Risks and test signals: failure is explicit if the final value is not exactly expected. Other risks include starvation from repeated rollback under high contention, missing cursor/session cleanup in worker threads, or table-type option changes. Passing prints the operation count and elapsed processor seconds.
