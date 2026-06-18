# sources/storage-engines/wiredtiger/test/suite/test_readonly02.py

Purpose: validates readonly mode rejects illegal configuration and unsafe recovery cases: opening a new database readonly, opening an unclean copy readonly, and combining readonly with log zero-fill.

Important APIs and types: `copy_wiredtiger_home`, `wiredtiger_open`, `assertRaisesWithMessage`, readonly connection configs, `os.mkdir`, and `wiredtiger.WiredTigerError`.

Control flow: during first connection open, it creates a separate directory and asserts `readonly=true` cannot create/open it because required files are absent. The test creates a logged table and inserts data, copies the home as an unclean backup and asserts readonly open needs recovery, then closes and reopens readonly with `log=(enabled,zero_fill=true)` expecting invalid argument.

State and persistence behavior: the test confirms readonly mode never performs creation or recovery writes and rejects logging settings that imply file modification.

Dependencies and integration points: connection open validation, logging configuration, unclean-home detection, filesystem copy helper, and platform-specific error text.

Risks: error message substrings vary by OS; the source handles POSIX versus non-POSIX missing-file wording.

Test signals: expected `WiredTigerError` messages match `No such file` or platform equivalent, `needs recovery`, and `Invalid argument`.
