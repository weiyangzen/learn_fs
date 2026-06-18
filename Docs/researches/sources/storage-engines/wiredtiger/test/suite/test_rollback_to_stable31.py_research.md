# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable31.py

Purpose: documents and tests RTS behavior when no stable timestamp has ever been set. It compares runtime RTS with recovery-time RTS after crash, with and without checkpoint.

Important APIs/types/functions: extends the RTS base; uses `SimpleDataSet`, `large_updates`, `check`, optional `session.checkpoint`, `simulate_crash_restart`, and `conn.rollback_to_stable`. Scenarios vary row/column format, checkpoint mode, recovery/runtime mode, and worker counts.

Control flow: creates a table without setting oldest/stable, writes values at timestamps 10/20/30, optionally checkpoints, then either simulates crash/recovery or runs explicit RTS. It checks visibility at timestamps 5/15/25/35 based on mode.

State and persistence behavior: runtime RTS should do nothing when no stable timestamp exists. Recovery without checkpoint can lose all uncheckpointed content after crash; recovery with checkpoint preserves checkpointed timestamped data because there is no stable bound for RTS to enforce.

Dependencies and integration points: integrates crash simulation and checkpoint persistence semantics, not just RTS cleanup.

Risks: the expected result differs sharply between crash and runtime paths; future changes to recovery handling of absent stable timestamps must update the documented expectations.

Test signals: explicit value/row-count checks for each mode and checkpoint combination.
