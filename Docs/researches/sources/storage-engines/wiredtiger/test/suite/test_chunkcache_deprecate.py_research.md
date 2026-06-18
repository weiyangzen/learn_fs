# sources/storage-engines/wiredtiger/test/suite/test_chunkcache_deprecate.py

Purpose: verifies deprecated chunk cache configuration is rejected or warned according to whether it attempts to enable or disable the removed feature.

Important APIs and types: `wiredtiger_open`, `open_conn`, `close_conn`, `assertRaisesWithMessage`, `expectedStdoutPattern`, and `wiredtiger.WiredTigerError`.

Control flow: close the default connection; attempt to open with `chunk_cache=(enabled=true)` and expect a deprecation error; reopen normally for teardown. A second test closes the connection and opens with `enabled=false`, expecting a deprecation warning on stdout.

State and persistence behavior: no data is created. The state under test is connection configuration acceptance and messaging for deprecated options.

Dependencies and integration points: directly exercises WiredTiger connection config parsing and compatibility/deprecation path.

Risks: stdout warning text is part of the contract and may be brittle. The disabled-warning test does not explicitly reopen normally afterward, relying on test lifecycle cleanup.

Test signals: enabling chunk cache raises; disabling chunk cache prints the expected deprecation warning while opening succeeds.
