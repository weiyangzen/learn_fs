<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/dbwrap_torture.c -->
# sources/user-network-fs/samba/source3/utils/dbwrap_torture.c

## Purpose
`dbwrap_torture.c` is a simple stress tool for persistent dbwrap/TDB transaction semantics. Multiple instances can update a shared counter array keyed by `"testkey"` and verify counters are monotonically increasing.

## Important APIs, types, and functions
- Global options include `timelimit`, `torture_delay`, `verbose`, `no_trans`, `db_name`, and `unsafe_writes`.
- `print_counters()` displays the last observed counter array.
- `each_second()` periodically prints counters for node 0 in non-verbose mode.
- `check_counters()` verifies no counter decreases and updates `old_data`.
- `do_sleep()` injects delays between operations for race amplification.
- `test_store_records()` performs the transaction/fetch-lock/increment/store/commit loop.
- `main()` parses options, opens the db, determines the local virtual node number, and runs the test.

## Control flow
After command-line setup, the program opens the test database. If running outside a cluster, it forces VNN 0. The test loop runs until `timelimit` expires or forever when zero. Each iteration optionally starts a dbwrap transaction, fetch-locks `testkey`, grows the record to include this node's counter, increments that counter, stores the record, commits if needed, checks monotonicity for verbose or node 0, and sleeps at configured points.

## State and persistence behavior
The database record `testkey` persists a packed array of `uint32_t` counters. `old_data` is process-local history used for monotonic checks. `--no-trans` switches to fetch-lock/record-store without explicit transactions and uses `TDB_CLEAR_IF_FIRST|TDB_INCOMPATIBLE_HASH`; `--unsafe-writes` uses `TDB_NOSYNC`.

## Dependencies and integration points
The file depends on dbwrap/dbwrap_open, transactions, record locks, Samba command-line/loadparm, messaging, tevent timers, cluster node helpers `get_my_vnn()`/`set_my_vnn()`, and util_tdb helpers. It is a diagnostic for dbwrap backends and CTDB-like multi-node behavior.

## Risks and edge cases
- Counter data is raw host-endian `uint32_t` array and not portable storage.
- `old_data` starts empty; printing before enough data exists can show no counters.
- `unsafe_writes` and `no_trans` deliberately weaken persistence/atomicity and are for torture scenarios only.
- The event timer is scheduled but the main loop is synchronous and sleeps, so timer progress depends on operations that pump events elsewhere being absent; this is mostly a diagnostic print hook.

## Test signals
The key signal is final `SUCCESS!` versus `The test FAILED`. Running several instances against the same db with delays increases coverage of locking and transaction behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/dbwrap_torture.c -->
