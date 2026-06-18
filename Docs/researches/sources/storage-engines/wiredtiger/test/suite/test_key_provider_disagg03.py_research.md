# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg03.py

Purpose: verifies the key-provider `set_key` push API persists a supplied key once the stable timestamp reaches that key's timestamp.

Important APIs and functions: uses `wiredtiger.CryptKeys`, `conn.get_key_provider().set_key`, PALite SQLite inspection helpers, and the test key-provider extension configured with `version=1`. It validates page id/version in the turtle metadata and counts key-provider pages.

Control flow: the test skips non-PALite storage, populates a small layered dataset, pushes a key at timestamp 1, advances stable timestamp to 1, checkpoints, then verifies at least one key-provider page exists and turtle metadata points to the expected main KEK page/version.

State and persistence behavior: pushed keys are pending until stable timestamp selection. Checkpoint persists the selected pushed key into the key-provider store and updates metadata.

Dependencies and integration points: integrates disaggregated storage, key-provider extension version 1, stable timestamp semantics, `CryptKeys`, checkpoint, and PALite SQLite validation.

Risks and edge cases: only one pushed key and timestamp are tested here. It relies on hard-coded special file IDs and page-data regex.

Test signals: `set_key` returns 0; key-provider page count is at least one; metadata validates page id 1 and version 1.
