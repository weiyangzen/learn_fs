# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor10.py

Purpose: tests layered cursor behavior around prepared update conflicts, especially preserving enough cursor/key state for retry or opposite-direction movement after `WT_PREPARE_CONFLICT`.

Important APIs/types/functions: uses `preserve_prepared=true`, `prepare_transaction`, `prepared_id_str`, commit/rollback scenarios, read timestamps, `cursor.search_near`, `next`, `prev`, `get_key`, and prepare conflict assertions.

Control flow: helper `setup_table_with_data` creates integer-key layered data and commits at timestamp 20. `prepare_key_in_separate_session` opens another session, writes a key, and prepares at timestamp 50. `test_search_near_key_preserved_on_prepare_conflict` searches near a prepared key 2, expects an error, checks key remains 2, then either commits and retries successfully or rolls back. `test_next_key_preserved_on_prepare_conflict` positions at key 1, `next()` hits prepared key 2, `get_key` requires key set, then `prev()` returns key 1; commit path then `next()` returns key 2. `test_prev_key_preserved_on_prepare_conflict` mirrors this from key 5 and prepared key 4.

State and persistence behavior: prepared updates are visible as conflicts to timestamp 60 readers until resolved. Cursor state after conflict must remain recoverable and directionally consistent.

Dependencies/integration points: prepared transaction engine, layered cursor search/iteration, transaction timestamps, error handling, and prepared commit/rollback resolution.

Risks: assertions use generic `WiredTigerError` for conflict rather than checking exact code/message in all cases. Commit path includes a `breakpoint()` call in one test, which may be harness-specific.

Test signals: pass means search_near/next/prev handle prepare conflicts without losing position semantics and can continue correctly after resolution.
