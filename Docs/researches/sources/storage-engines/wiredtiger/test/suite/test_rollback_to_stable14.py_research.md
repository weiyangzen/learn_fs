# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable14.py

Purpose: stresses RTS recovery of chains containing full updates plus `wiredtiger.Modify` deltas. It includes three variants: normal modify rollback, repeated modifies at the same timestamp, and append-style modify chains. Formats are column and integer row store, with prepared/non-prepared scenarios.

Important APIs/types/functions: uses helper `large_updates`, `large_modifies`, `check`, local `mod_val`-derived expected strings, `checkpoint_thread`, `simulate_crash_restart`, `stat.conn.txn_rts_hs_restore_updates`, `txn_rts_hs_removed`, `txn_rts_sweep_hs_keys`, and pages-visited counters.

Control flow: creates a base value at timestamp 20, applies multiple byte modifications at 30/40/50/60, advances stable to include part of the chain, checkpoints while applying newer modifications, restarts, and verifies every historical read reconstructs the correct string. Same-timestamp and append variants alter modify ordering and stable point.

State and persistence behavior: requires RTS to reconstruct stable full values from history-store update/modify chains rather than only full updates. Checkpoint races are used to persist history before recovery. Prepared mode skips some runtime combinations where uncommitted prepared transactions would make RTS illegal.

Dependencies and integration points: depends on `wiredtiger.Modify` behavior exposed by the shared helper, threaded checkpoint support, recovery helper, and detailed RTS history-store statistics.

Risks: modify chains are vulnerable to base-value selection, order errors, and same-timestamp edge cases. Background checkpoint timing can change exact `hs_removed` versus sweep counts, so the test uses combined lower bounds.

Test signals: exact reconstructed values at timestamps 20/30/40/50/60, zero explicit RTS calls on recovery, `hs_restore_updates == nrows`, no key restoration/removal, and positive history-store cleanup/visited pages.
