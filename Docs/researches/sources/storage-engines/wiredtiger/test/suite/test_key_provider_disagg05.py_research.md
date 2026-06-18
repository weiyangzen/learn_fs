# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg05.py

Purpose: tests selection of pushed keys across checkpoints for key-provider version 1, including draining multiple pending keys and selecting the highest key at or below stable timestamp.

Important APIs and functions: `key_provider_pages` reads PALite key-provider pages via SQLite, extracts the key bytes by parsing the crypt header size, and returns rows ordered by LSN. `key_for` encodes the timestamp into key bytes; `push_key` calls `conn.get_key_provider().set_key` with `CryptKeys`.

Control flow: `test_multiple_pushes_across_checkpoints` pushes keys 1-3, advances stable to 3, writes a row, checkpoints, and validates key 3; then pushes/validates keys 4 and 5 in separate checkpoints. `test_select_highest_at_or_below_stable` pushes keys 1-3, advances stable only to 2, checkpoints and validates key 2, then advances stable to 3 and validates key 3 on the next checkpoint.

State and persistence behavior: key-provider state includes a pending queue of pushed keys plus persisted pages. Checkpoint should persist the latest eligible key at or below stable and leave later keys pending.

Dependencies and integration points: integrates PALite SQLite storage, key-provider extension `version=1,key_expires=0`, `CryptKeys`, stable timestamp selection, layered tables, and checkpoint.

Risks and edge cases: byte parsing assumes crypt-header layout and offset 6 contains header size. Only PALite is validated.

Test signals: latest key-provider page has page id 1 and key bytes matching the expected timestamp after each checkpoint.
