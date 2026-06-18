# sources/storage-engines/wiredtiger/test/csuite/wt8963_insert_stress/main.c

## Purpose
WT-8963 stresses concurrent random-key insert lists with many threads and large memory pages, then verifies the resulting table.

## Important APIs, Types, and Functions
- Uses `NUM_THREADS=110`, `THREAD_NUM_ITERATIONS=200000`, `KEY_MAX=UINT32_MAX`.
- Table config sets `memory_page_image_max=50MB` and row or column key format from `TEST_OPTS`.
- `thread_insert_race` opens its own session/cursor, waits on an atomic ready counter, and inserts random keys.
- `set_key` and `set_value` wrap variadic cursor calls for correct typing.

## Control Flow
The test parses options, defaults to 110 threads and row-store, opens a 4 GiB cache database, creates the table, starts all insert threads, joins them, closes/reopens the connection so verify can get exclusive access, verifies the table, scans all records to count them, prints count and duration, and cleans up.

## State and Persistence Behavior
The persistent table contains random unique or duplicate inserts depending on generated keys and WiredTiger semantics for the key format. The barrier ensures all threads begin inserting at roughly the same time, increasing insert-list contention.

## Dependencies and Integration Points
The test depends on pthreads, atomic operations, large cache availability, and `session->verify`. It lives in C suite because it needs validation overrides not available in the C++ suite according to the comment.

## Risks and Test Signals
Insert or verify failure indicates concurrency or insert-list corruption. Because keys are random, duplicate-key behavior affects final count. The workload is intentionally heavy: 22 million insert attempts with 110 threads and 4 GiB cache.
