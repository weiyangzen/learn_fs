# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable04.py

Purpose: ensures RTS restores a full stable update from history store when the update chain includes many modify records and full updates.

Important APIs and types: helper `mod_val`, base helper methods `large_updates`, `large_modifies`, `evict_cursor`, `check`, `conn.rollback_to_stable`, dryrun/evict/in-memory/prepare/thread scenarios, and RTS statistics including HS sweep counters.

Control flow: it writes value A at timestamp 20, applies modifies Q/R/S at 30/40/50, optionally evicts, then writes/modified many later generations through timestamp 140. Stable is set to 40 for prepared mode or 30 otherwise. After checkpoint and RTS, it verifies the stable modified value Q is visible at timestamp 30 and at a future timestamp for real RTS, while dryrun retains the latest value at future timestamp.

State and persistence behavior: RTS must not reconstruct stable state from a partial modify chain incorrectly; it must use a full update or correctly resolved history value. Later full updates and modifies are removed or counted.

Dependencies and integration points: modify chains, history store, eviction, RTS dryrun, in-memory mode, prepared timestamp handling, and statistics.

Risks: this is sensitive to full-update versus modify reconstruction semantics. Statistics expect at least eleven rolled-back generations per row.

Test signals: value checks across every generation pass before RTS; after RTS, non-dryrun future reads return `value_modQ`; dryrun retains latest `value_modZ`; RTS counters match mode-specific branches.
