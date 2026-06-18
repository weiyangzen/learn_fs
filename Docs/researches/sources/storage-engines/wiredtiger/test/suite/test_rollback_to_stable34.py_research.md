# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable34.py

Purpose: validates RTS rollback of fast-delete/truncate operations, including recovery and runtime modes, optional second checkpoint, prepared/non-prepared variants, and column/integer/string row formats.

Important APIs/types/functions: extends RTS base; sets snapshot isolation and logging disabled. Defines `mkdata`, `evict`, and `checkx`. Uses cursor `truncate`, prepared transaction support, `simulate_crash_restart`, `conn.rollback_to_stable`, `stat.dsrc.rec_page_delete_fast`, and worker thread scenarios.

Control flow: writes baseline data at 20 and updated data at 30, evicts pages, sets stable to 25, checkpoints, truncates most of the table at 35 (optionally prepared), verifies fast-delete stats, optionally checkpoints again, then either crashes/restarts or calls runtime RTS. It verifies reads at 20/30 after rollback.

State and persistence behavior: the unstable fast-delete must be undone so all original keys remain visible. Recovery may need to instantiate fast-deleted pages and apply history to restore them.

Dependencies and integration points: integrates fast truncate, eviction, checkpoint, prepare, recovery, and RTS. It covers both fixed column keys and string row keys.

Risks: runtime RTS with uncommitted prepared truncates is skipped because RTS rejects unresolved prepared transactions. Fast-delete stats depend on page layout and may fail if the table does not produce fast-deleted pages.

Test signals: positive fast-delete stats, successful rollback/recovery, and `checkx` validating all `nrows` keys at historical timestamps.
