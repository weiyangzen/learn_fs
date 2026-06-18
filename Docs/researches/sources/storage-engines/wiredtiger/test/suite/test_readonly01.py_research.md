# sources/storage-engines/wiredtiger/test/suite/test_readonly01.py

Purpose: broad read-only mode smoke test ensuring data can be read after reopening with `readonly=true` across file/table and row/variable-length formats, logging modes, base config modes, and optional directory chmod.

Important APIs and types: `suite_subprocess`, `make_scenarios`, `conn_config`, `close_reopen`, `readonly`, `os.chmod`, `open_cursor`, and scenario matrices for `config_base`, directory permissions, logging, and URI/table type.

Control flow: the test creates a table or file object, inserts 10,000 integer values, closes the original connection, optionally makes the directory read-only on POSIX, reopens with `readonly=true`, scans all records, and verifies key/value order.

State and persistence behavior: the persisted table data must be fully readable without modifying the home. Logging can be enabled or disabled; base config can be on or off.

Dependencies and integration points: connection open configuration, filesystem permissions, logging, table/file object creation, and cursor iteration.

Risks: POSIX permission behavior can differ across environments; the test wraps readonly directory cases with an expected `Permission` stderr pattern.

Test signals: all 10,000 entries are read back with expected values, or permission errors are expected in chmod scenarios.
