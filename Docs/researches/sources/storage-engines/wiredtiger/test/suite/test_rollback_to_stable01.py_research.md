# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable01.py

Purpose: tests rollback-to-stable clears a newer remove operation and restores stable data, with variants for row/column formats, in-memory mode, prepared updates, dry run, and RTS worker threads.

Important APIs and types: `test_rollback_to_stable_base`, `large_updates`, `large_removes`, `check`, `conn.rollback_to_stable`, `stat.conn.txn_rts*` counters, and `make_scenarios`.

Control flow: it writes 10,000 rows at timestamp 10, verifies them, removes all keys at timestamp 20, verifies the table appears empty, sets stable to 20 for prepared mode or 10 otherwise, checkpoints when not in-memory, runs RTS with dryrun/thread options, checks final visibility, and validates RTS statistics.

State and persistence behavior: the stable state should contain the original value. Non-dryrun restores it after rolling back the remove; dryrun leaves the remove in place. In-memory mode has different accounting because there is no disk history restoration.

Dependencies and integration points: RTS, prepared timestamp convention in the base helper, history store/disk restore, in-memory mode, dryrun accounting, and worker threading.

Risks: statistic expectations branch by dryrun and in-memory, so changes to RTS accounting can break the test even if data behavior is correct.

Test signals: data visibility matches dryrun versus real RTS expectations, calls equal 1, pages visited is positive, and aborted/restored dryrun counters match row count.
