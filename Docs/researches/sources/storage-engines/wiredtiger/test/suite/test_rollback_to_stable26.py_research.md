# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable26.py

Purpose: tests recovery RTS when a checkpoint races with prepared or unprepared updates, optional history-store removes, and an optional prepared remove. It validates history-store restoration and cleanup after crash.

Important APIs/types/functions: extends the RTS base; imports `checkpoint_thread` and `simulate_crash_restart`; defines `evict_cursor`; uses `large_updates`, `large_removes`, prepared transactions, `stat.conn.checkpoint_state`, and stats including `txn_rts_hs_removed`, `txn_rts_hs_restore_updates`, and key removal counters.

Control flow: writes values at 20 and 30, optionally removes at 40, opens a prepared transaction at 50 that updates or removes one key, sets stable to 40, starts a checkpoint thread and waits for checkpoint state, writes value D at 60, restarts, verifies stable values, and writes value E after recovery to ensure the table remains usable.

State and persistence behavior: combines stable history-store records, prepared state, and concurrent checkpoint persistence. Recovery should restore exactly `nrows` updates from the history store and remove obsolete history-store entries.

Dependencies and integration points: integrates checkpoint threading, prepare handling, eviction/reconciliation, recovery RTS, and statistics.

Risks: checkpoint waiting is timing-sensitive. Prepared remove branches are subtle because unresolved prepared operations can block runtime RTS but recovery must resolve persisted state safely.

Test signals: post-restart data checks, `keys_removed == 0`, `hs_restore_updates == nrows`, `hs_removed == nrows`, then successful post-recovery writes and reads.
