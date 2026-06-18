<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp27.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp27.py

Purpose: Tests rollback timestamp API validation for prepared and non-prepared transactions, with and without `preserve_prepared`.

Important APIs/types/functions: Two classes cover `preserve_prepared=false` default and `preserve_prepared=true` with `precise_checkpoint=true`. APIs include `rollback_transaction('rollback_timestamp=...')`, `prepare_transaction`, `timestamp_transaction('rollback_timestamp=...')`, `conn.set_timestamp('stable_timestamp=...')`, and begin transaction `roundup_timestamps=(prepare=true)`.

Control flow: Non-prepared transactions must reject rollback timestamps. Prepared transactions can set a rollback timestamp. With preserved prepared transactions, rollback timestamp must be newer than stable and cannot be combined with commit or durable timestamps. The test also rejects prepare timestamp roundup under preserve-prepared.

State and persistence behavior: The state under test is prepared transaction metadata and stable timestamp ordering. No table data is needed; the API validation occurs on transaction state.

Dependencies and integration points: Integrates transaction prepare/rollback timestamp parsing, stable timestamp validation, preserve-prepared connection configuration, and precise checkpoint mode.

Risks: The class contains two methods with the same Python name `test_rollback_timestamp_with_commit_timestamp`; the second definition shadows the first, so only the durable-timestamp variant actually runs. That is a coverage risk for the combined rollback+commit config case.

Test signals: Expected `WiredTigerError` messages for non-prepared use, not-newer-than-stable rollback timestamps, invalid combined timestamp options, and prohibited prepare roundup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp27.py -->
