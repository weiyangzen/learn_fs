# sources/storage-engines/wiredtiger/test/suite/test_encrypt03.py

Purpose: tests encryption error handling when table-level encryption is requested but system encryption is `none`.

Important APIs and control flow: scenario creates a table with system encryption `none` and a table encryption setting based on `rotn` plus a key-id argument. `conn_extensions` loads both requested encryptors. `conn_config` applies system encryption. The test builds a table-create string with `encryption=(name=...)` and expects `session.create` to raise `WiredTigerError` matching `/to be set: Invalid argument/`.

State and persistence: no valid table should be created in the error case. The focus is configuration validation before durable data exists.

Dependencies and integration: uses `wiredtiger`, `wttest`, `make_scenarios`, and encryptor extension loading.

Risks and test signals: failures indicate encryption configuration validation changed. Comments note a different inherited-system-encryption case is now permitted and intentionally not tested here.
