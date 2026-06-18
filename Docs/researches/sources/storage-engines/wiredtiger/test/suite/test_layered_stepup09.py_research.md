# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup09.py

## Purpose
Verifies stable cursor lifecycle when a layered cursor opened on a follower is reused after that connection becomes leader.

## APIs, Types, And Functions
Defines module-level operation functions for insert, update, search, search_near, next, prev, remove, reserve, modify, and largest_key. The test class uses overwrite and no-overwrite cursor scenarios, connection statistics `layered_curs_open_stable` and `layered_curs_reopen_stable`, and role reconfiguration.

## Control Flow, State, And Persistence
One test advances the follower to a checkpoint, opens the stable cursor through a read, resets it, closes the old leader, promotes the follower, then uses the same cursor in a rollback transaction and expects a stable-cursor reopen. The second test never opens stable before step-up and expects first post-step-up use to open it once without a reopen. Inserted ingest data keeps the cursor active while stable state changes.

## Dependencies, Integration, Risks, And Test Signals
Depends on layered cursor statistics, disaggregated checkpoint advancement, and cursor operation semantics. Risks are leaving a read-only stable cursor active after promotion, reopening when unnecessary, or operation-specific cursor breakage. Signals are exact statistic counters after the selected operation.
