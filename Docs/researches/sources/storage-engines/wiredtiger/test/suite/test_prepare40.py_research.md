# sources/storage-engines/wiredtiger/test/suite/test_prepare40.py

## Purpose

Regression test that checkpoint after opening a backup with prepared updates does not crash when a prepared transaction is later rolled back with rollback timestamp greater than stable.

## Important APIs, Control Flow, and State

With precise checkpoint and preserve-prepared enabled, the test commits keys 1 and 2 at timestamp 60, prepares keys 3 to 5 at timestamp 100 with prepared ID 123, advances stable to 150, and checkpoints to write prepared cells. It force-evicts committed keys to hit on-disk prepare resolution, rolls back at timestamp 200, and checkpoints from a new session. Non-disagg expects `rec_time_window_prepared`; disagg expects no page delta write.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared checkpoint stats, debug page eviction, hook detection, and rollback timestamp handling. Risks are crashes or wrong reconciliation after prepared cells were written then rolled back while rollback remains unstable. Signals are successful post-rollback checkpoint with expected stats.
