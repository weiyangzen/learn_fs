# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable10.py

Purpose: stresses recovery-time RTS, history-store cleanup, checkpoint races, and prepared transactions across two tables. It has one general crash/restart test and a dedicated prepared transaction variant that copies the home before committing prepared updates.

Important APIs/types/functions: `test_rollback_to_stable10` extends the RTS base, uses `checkpoint_thread`, `simulate_crash_restart`, `copy_wiredtiger_home`, `threading.Event`, `time.sleep`, `SimpleDataSet`, `large_updates`, `check`, and `check_hs_stats`. Connection config enables history-store checkpoint delay timing stress, statistics logging, and RTS verbosity.

Control flow: both tests create two tables, write values at 20/30/40/50, advance stable to include 50/60 depending on prepare, start a checkpoint thread, perform more updates while checkpointing, then restart. The prepared variant performs an initial checkpoint, starts prepared transactions on both tables, copies the home while history-store content is present, commits prepared transactions in the original home, and opens the copied home to force recovery.

State and persistence behavior: the tests depend on persisted history-store pages and partial checkpoints. `check_hs_stats` expects recovery RTS to visit pages and remove or sweep history-store entries while not removing keys or restoring keys. The prepared variant checks history-store file size before and after restart.

Dependencies and integration points: integrates threaded checkpoint machinery, recovery simulation, history-store statistics, and prepare timestamp semantics. It is a concurrency regression for interactions among checkpoint, history store, prepared updates, and RTS.

Risks: inherently timing-sensitive; checkpoint timing determines whether work is counted in `txn_rts_hs_removed` or `txn_rts_sweep_hs_keys`. The test accounts for this by asserting the sum is positive rather than exact.

Test signals: data visibility after restart, positive history-store processing, zero explicit RTS calls, no key removals/restorations, positive pages visited, and positive on-disk history-store size in the prepared path.
