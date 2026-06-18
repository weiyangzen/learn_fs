# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor03.py

Purpose: minimal smoke test for layered table creation and cursor open/close.

Important APIs/types/functions: uses `disagg_test_class`, connection config with `verbose=[layered]`, `disaggregated=(role="leader")`, and `lose_all_my_data=true`; calls `session.create`, `session.open_cursor`, and `cursor.close`.

Control flow: creates a `layered:` table with string key/value formats, opens a cursor, then closes it.

State and persistence behavior: only table metadata and cursor handle lifecycle are exercised. No rows are inserted and no checkpoint is taken explicitly.

Dependencies/integration points: layered URI create path, disaggregated leader setup, cursor open path, and verbose layered logging.

Risks: very narrow coverage; it catches basic open/create regressions but not read/write or persistence issues.

Test signals: pass means a layered table can be created and opened with a cursor under the configured disaggregated leader connection.
