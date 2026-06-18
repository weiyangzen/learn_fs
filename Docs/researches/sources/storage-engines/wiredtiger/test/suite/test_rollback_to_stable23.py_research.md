# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable23.py

Purpose: validates recovery RTS over modify chains and verifies values using explicit `set_key` cursor access. It covers column and integer-row keys plus prepared/non-prepared updates.

Important APIs/types/functions: extends the RTS base; defines `check_with_set_key` to read each key by direct lookup instead of cursor iteration. Uses `large_updates`, `large_modifies`, `session.checkpoint`, `simulate_crash_restart`, and stats including `txn_rts_hs_restore_updates` and `txn_rts_hs_removed`.

Control flow: writes a full base value at 20, applies byte modifications at 30/40/50/60, advances stable to 60 for prepared or 50 otherwise, checkpoints, restarts, then checks direct lookups for expected values at each timestamp up to stable.

State and persistence behavior: recovery RTS must reconstruct stable values from update/modify chains after checkpointed unstable content. Direct lookup checks ensure point-search behavior matches iteration behavior tested elsewhere.

Dependencies and integration points: depends on `wiredtiger.Modify` through shared helper logic, recovery simulation, and history-store restore stats.

Risks: byte-offset modify expectations are brittle if value construction changes. Prepared timestamp shifts must preserve the correct stable boundary.

Test signals: point-lookup checks for every key at historical timestamps, `hs_restore_updates == nrows`, and history-store removal lower bounds, with prepared branches allowing different cleanup counts.
