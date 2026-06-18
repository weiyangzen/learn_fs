# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg01.py

Purpose: tests basic disaggregated key-provider behavior with PALite storage, including key metadata persistence across reopen and crash/restart.

Important APIs and functions: decorated with `@disagg_test_class`; scenarios combine PALite disaggregated storage and crash versus reopen. `conn_extensions` loads the test `key_provider` extension with `early_load=true` and configurable `key_expires`. SQLite helpers read PALite `pages_*.db` files via the build `sqlite3`.

Control flow: the test skips non-PALite scenarios, populates a layered dataset, checkpoints twice and validates key-provider metadata, adds more rows, changes `key_expire` to 12 hours, then either simulates crash/restart or reopens the connection. It validates the metadata page and key-provider/turtle row counts, adds more data, checkpoints, and validates again.

State and persistence behavior: the main persisted state is the main KEK page in PALite special key-provider/turtle tables. Metadata must record page id 1 and expected version 1, and key-provider rows must track or exceed shared metadata rows depending on expiry.

Dependencies and integration points: integrates disaggregated storage helpers, PALite SQLite layout, key-provider extension, layered table data, checkpoint, reopen, and crash recovery.

Risks and edge cases: uses hard-coded PALite special file IDs and regex parsing of page data. It skips non-PALite backends, so coverage is backend-specific.

Test signals: dataset checks pass; SQLite metadata validates page id/version; key-provider row counts match expectations after reopen/crash and checkpoint.
